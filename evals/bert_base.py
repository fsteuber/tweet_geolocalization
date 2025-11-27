from sklearn.preprocessing import OneHotEncoder
from transformers import AutoTokenizer, BertForSequenceClassification, EvalPrediction, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import train_test_split
import torch
import wandb

files = ["en.test1", "en.train1"]

labels = []
texts = []
for file in files:
    with open(file, "r") as f:
        for line in f:
            label, *text =  line.replace("\n", "").split(" ")
            text = " ".join(text)
            labels.append(label)
            texts.append(text)
            
labels_num = sorted([int(x.replace("__label__", "")) for x in list(set(labels))])

id2label = {idx:"__label__"+str(label) for idx, label in enumerate(labels_num)}
label2id = {"__label__"+str(label):idx for idx, label in enumerate(labels_num)}

labels = [label2id[x] for x in labels]

##########################
#limit = 100000
limit = 1000000
labels = labels[:limit]
texts = texts[:limit]
##########################

model_name = "google-bert/bert-base-uncased"
max_length = 512
model = BertForSequenceClassification.from_pretrained(model_name, num_labels = len(id2label), output_attentions = False, output_hidden_states = False)
tokenizer = AutoTokenizer.from_pretrained(model_name, do_lower_case=False, max_length = max_length, TOKENIZERS_PARALLELISM=True)

train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=.2)

train_encodings = tokenizer(list(train_texts), truncation=True, padding=True, max_length = max_length)
test_encodings = tokenizer(list(test_texts), truncation=True, padding=True,  max_length = max_length)

class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = list(labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = CustomDataset(train_encodings, train_labels)
test_dataset = CustomDataset(test_encodings, test_labels)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)

    acc = accuracy_score(labels, preds)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(labels, preds, average="macro", zero_division=0)
    p_micro, r_micro, f1_micro, _ = precision_recall_fscore_support(labels, preds, average="micro", zero_division=0)

    try:
        probs = torch.softmax(torch.tensor(logits), dim=-1).numpy()
        roc = roc_auc_score(labels, probs, multi_class="ovr")
    except Exception:
        roc = float("nan")

    return {
        "accuracy": acc,
        "precision_macro": p_macro,
        "recall_macro": r_macro,
        "f1_macro": f1_macro,
        "f1_micro": f1_micro,
        "roc_auc": roc,
    }

metric_name = "f1_macro"

output_dir = './out'
training_args = TrainingArguments(
    output_dir = output_dir,
    num_train_epochs=4,
    per_device_train_batch_size = 4,
    gradient_accumulation_steps = 16,    
    per_device_eval_batch_size= 8,
    eval_strategy = "epoch",
    save_strategy = "epoch",
    #learning_rate=1e-5,
    disable_tqdm = False, 
    load_best_model_at_end=True,
    weight_decay=0.01,
    logging_steps = 8,
    #fp16 = True,
    fp16 = False,
    dataloader_num_workers = 8,
    metric_for_best_model=metric_name,
    run_name="out"
)

trainer = Trainer(
    model=model,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=train_dataset,
    eval_dataset=test_dataset
)

trainer.train()

trainer.save_model()

tokenizer.save_pretrained(output_dir)