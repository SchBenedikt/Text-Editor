import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer


# load the model(Around 8 seconds)
peft_model_id = "dfurman/Falcon-7B-Chat-v0.1"
config = PeftConfig.from_pretrained(peft_model_id)

#Set the configs for the model(do not change this)
model = AutoModelForCausalLM.from_pretrained(
    config.base_model_name_or_path,
    return_dict=True,
    device_map={"":0},
    trust_remote_code=True,
    load_in_8bit=False,#Set it true if you have pip installed bits and bytes and other libraries(see the error).
)

#Load the tokenizer for the model(faster)
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
tokenizer.pad_token = tokenizer.eos_token

#Load main model
model = PeftModel.from_pretrained(model, peft_model_id)

#For Q&A
#prompt = """<human>: My name is Celsia. Write a short email to my closest friends inviting them to come to my home on Friday for a dinner party, I will make the food but tell them to BYOB.
#<bot>:"""
#For completing sentence

def generate_with_prompt(prompt):
        
    prompt = """<Celsia>: So that's why the property of Phathocyanine allows electricity"""
    
    #Set the batch for the prompt sent to the model
    batch = tokenizer(
        prompt,
        padding=True,
        truncation=True,
        return_tensors='pt'
    )
    #Set it as to cuda if you have them, else use CPU is the best way.
    batch = batch.to('cpu')
    
    #Generate the output sequence
    output_tokens = model.generate(
        inputs=batch.input_ids, 
        max_new_tokens=5,#The number of words or special characters generated
        do_sample=False,#Makes an extra example(slower)
        use_cache=True,#Faster
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
    result = generated_text.split("<Celsia>: ")[1].split("<bot>: ")[-1]
    print(result)
    return result

#The training set
train = []

def finetune_lora(train):
    '''define the load function for loading the lora onto the model
    and continue to fine tune for the model'''
    return
