import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

# load the model(Around 8 seconds)
peft_model_id = "dfurman/Falcon-7B-Chat-v0.1"
config = PeftConfig.from_pretrained(peft_model_id)

model = AutoModelForCausalLM.from_pretrained(
    config.base_model_name_or_path,
    return_dict=True,
    device_map={"":0},
    trust_remote_code=True,
    load_in_8bit=False,
)

tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
tokenizer.pad_token = tokenizer.eos_token

model = PeftModel.from_pretrained(model, peft_model_id)

#For Q&A
#prompt = """<human>: My name is Celsia. Write a short email to my closest friends inviting them to come to my home on Friday for a dinner party, I will make the food but tell them to BYOB.
#<bot>:"""
#For completing sentence
prompt = """<Celsia>: So that's why the property of Pythalocyanine allows electricity"""

batch = tokenizer(
    prompt,
    padding=True,
    truncation=True,
    return_tensors='pt'
)
batch = batch.to('cpu')

output_tokens = model.generate(
    inputs=batch.input_ids, 
    max_new_tokens=5,
    do_sample=False,
    use_cache=True,
    temperature=1.0,
    top_k=50,
    top_p=1.0,
    num_return_sequences=1,
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id,
    bos_token_id=tokenizer.eos_token_id,
)

generated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
# Inspect message response in the outputs
print(generated_text.split("<Celsia>: ")[1].split("<bot>: ")[-1])
