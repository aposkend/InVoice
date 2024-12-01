import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from transformers import BertTokenizerFast, AutoModel
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from joblib import dump, load

# 1. 資料前處理
# 載入資料並進行標籤編碼
df = pd.read_csv("/Users/willa/Desktop/畢專/MyData .csv")
LE = LabelEncoder()
df['label'] = LE.fit_transform(df['item_tag'])
dump(LE, 'label_encoder_80_keras.joblib')

# 設置設備，MPS 為 Apple Silicon 上的 GPU 支持
device = torch.device('mps' if torch.backends.mps.is_built() else 'cpu')
print(device)

# Bert pretrain
tokenizer = BertTokenizerFast.from_pretrained('ckiplab/bert-base-chinese')
model = AutoModel.from_pretrained('ckiplab/bert-base-chinese').to(device)

# 載入數據集
dataset = pd.read_csv("/Users/willa/Desktop/畢專/MyData .csv")

# BERT embesdding 提取
processed_data = []
for _, sample in dataset.iterrows():
    item_name = sample["item_name"]
    try:
        tokenized_inputs = tokenizer(text=item_name, padding=True, truncation=True, return_tensors="pt").to(device)
        with torch.no_grad():
            hidden_states = model(**tokenized_inputs).last_hidden_state
        cls_embedding = hidden_states[:, 0, :].cpu().numpy().squeeze()
        processed_data.append(cls_embedding)
    except Exception as e:
        print(f"Error processing item_name: {item_name}, error: {e}")

# 分割資料集為訓練集和驗證集
x_train, x_val, y_train, y_val = train_test_split(
    processed_data, df['label'], test_size=0.4, random_state=30, shuffle=False
)

print(f"Train samples: {len(x_train)}, Val samples: {len(x_val)}")


# 模型架構
def create_model(input_shape, num_classes):
    bert_embeddings_input = layers.Input(shape=input_shape, dtype=tf.float32, name="bert_embeddings_input")
    lay = layers.Dense(200, activation='relu')(bert_embeddings_input)
    lay = layers.Dropout(0.2)(lay)
    out = layers.Dense(num_classes, activation='softmax')(lay)
    model = models.Model(inputs=bert_embeddings_input, outputs=out)
    return model


# 創建模型
input_shape = processed_data[0].shape
num_classes = len(LE.classes_)
model = create_model(input_shape, num_classes)

# 設置回調函數
checkpoint = callbacks.ModelCheckpoint('model.keras', monitor='val_accuracy', save_best_only=True, verbose=1)
earlystopping = callbacks.EarlyStopping(monitor='val_accuracy', patience=5, verbose=1)

# 4. 模型訓練與驗證
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

train_sh = model.fit(
    np.array(x_train),
    np.array(y_train),
    validation_data=(np.array(x_val), np.array(y_val)),
    epochs=50, # 減少到更合理的epoch數
    callbacks=[checkpoint, earlystopping],
    batch_size=32,
    verbose=1
)

# 保存模型
model.save("final_model.h5")

# 5. 模型評估
test_loss, test_accuracy = model.evaluate(np.array(x_val), np.array(y_val))
print(f"Test Loss: {test_loss}, Test Accuracy: {test_accuracy}")
