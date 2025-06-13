import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# ========================
# 1. Load dan Preprocessing Data
# ========================
riasec_df = pd.read_csv("Dataset/interests_riasec_dataset.csv")
occupation_df = pd.read_csv("Dataset/occupation_dataset.csv")
occupation_df = occupation_df.rename(columns={'Code': 'O*NET-SOC Code'})
occupation_df = occupation_df[['O*NET-SOC Code', 'Job Family']].drop_duplicates()

# Pivot dan gabungkan job family
df_pivot = riasec_df[['O*NET-SOC Code', 'Title', 'Element Name', 'Data Value']] \
    .pivot_table(index=['O*NET-SOC Code', 'Title'], columns='Element Name', values='Data Value') \
    .reset_index()

# Gabungkan dengan job family
df_pivot = df_pivot.merge(occupation_df, on='O*NET-SOC Code', how='left')

# Simpan hasil merge
df_pivot.to_csv("Dataset/job_with_family.csv", index=False)

riasec_types = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
df_pivot = df_pivot[['O*NET-SOC Code', 'Title', 'Job Family'] + riasec_types]

scaler = StandardScaler()
riasec_scaled = scaler.fit_transform(df_pivot[riasec_types])

# Simpan scaler
joblib.dump(scaler, "Model/scaler.pkl")

# ========================
# 2. Model Embedding
# ========================
def create_embedding_model(input_dim=6, embedding_dim=16):
    inputs = tf.keras.Input(shape=(input_dim,))
    x = tf.keras.layers.Dense(64, activation='relu')(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(32, activation='relu')(x)
    outputs = tf.keras.layers.Dense(embedding_dim)(x)
    return tf.keras.Model(inputs, outputs)

embedding_model = create_embedding_model()

# ========================
# 3. Triplet Sampling
# ========================
def generate_triplets(data, n_triplets=10000):
    triplets = []
    for _ in range(n_triplets):
        anchor_idx = np.random.randint(len(data))
        anchor = data[anchor_idx]
        dists = np.linalg.norm(data - anchor, axis=1)
        positive_pool = np.where(dists < 1.0)[0]
        negative_pool = np.where(dists > 2.0)[0]
        if len(positive_pool) > 1 and len(negative_pool) > 0:
            positive_idx = np.random.choice(positive_pool)
            while positive_idx == anchor_idx:
                positive_idx = np.random.choice(positive_pool)
            negative_idx = np.random.choice(negative_pool)
            triplets.append((anchor, data[positive_idx], data[negative_idx]))
    return triplets

triplets = generate_triplets(riasec_scaled)
anchors = np.array([t[0] for t in triplets])
positives = np.array([t[1] for t in triplets])
negatives = np.array([t[2] for t in triplets])

# ========================
# 4. Triplet Loss
# ========================
def triplet_loss(margin=1.0):
    def loss(y_true, y_pred):
        anchor, positive, negative = y_pred[:, :16], y_pred[:, 16:32], y_pred[:, 32:]
        pos_dist = tf.reduce_sum(tf.square(anchor - positive), axis=1)
        neg_dist = tf.reduce_sum(tf.square(anchor - negative), axis=1)
        return tf.reduce_mean(tf.maximum(pos_dist - neg_dist + margin, 0.0))
    return loss

# ========================
# 5. Triplet Model Training
# ========================
input_anchor = tf.keras.Input(shape=(6,))
input_positive = tf.keras.Input(shape=(6,))
input_negative = tf.keras.Input(shape=(6,))
embedded_anchor = embedding_model(input_anchor)
embedded_positive = embedding_model(input_positive)
embedded_negative = embedding_model(input_negative)
merged_output = tf.keras.layers.Concatenate()([embedded_anchor, embedded_positive, embedded_negative])

triplet_model = tf.keras.Model(inputs=[input_anchor, input_positive, input_negative], outputs=merged_output)
triplet_model.compile(optimizer='adam', loss=triplet_loss())

history = triplet_model.fit(
    [anchors, positives, negatives],
    np.zeros(len(triplets)),
    epochs=20,
    batch_size=64,
    validation_split=0.2,
    verbose=1
)

# ========================
# 6. Simpan Model Embedding
# ========================
embedding_model.save("Model/embedding_model.keras")

# ========================
# 7. Plot Loss
# ========================
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training dan Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
