import spacy

nlp = spacy.load("en_core_web_sm")  # 加载预训练模型
text = "ZHANG TIANQIN, the partner of xxx."
doc = nlp(text)

for ent in doc.ents:
    print(ent.text, ent.label_)
