
import gradio as gr
import pandas as pd
from transformers import pipeline

# 1. Speech-to-Text model
stt_model = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")

# 2. Text-to-SQL model
text2sql_model = pipeline("text2text-generation", model="google/flan-t5-large")

# Mock database (Pandas DataFrame)
data = {
    "name": ["Alice", "Bob", "Charlie", "Diana"],
    "sales": [120, 90, 300, 150],
    "date": ["2025-07-01", "2025-07-03", "2025-07-02", "2025-07-01"]
}
df = pd.DataFrame(data)

# Sample queries with one word voice triggers
sample_queries = [
    "Alice",  # filter by name
    "sales greater than 100",  # numeric condition
    "date after 2025-07-01"    # date filter
]

def voice_to_sql(audio_file):
    # 1. Speech to text
    query_text = stt_model(audio_file)["text"]
    
    # 2. Natural language to SQL
    sql_prompt = f"Translate the following question into SQL: {query_text}"
    sql_query = text2sql_model(sql_prompt, max_length=100)[0]["generated_text"]

    # 3. Execute query (mock logic)
    try:
        if "sales" in sql_query and ">" in sql_query:
            threshold = int(sql_query.split(">")[-1].strip().split()[0])
            result = df[df["sales"] > threshold]
        elif "Alice" in sql_query:
            result = df[df["name"].str.contains("Alice")]
        elif "date" in sql_query and "2025-07-01" in sql_query:
            result = df[df["date"] > "2025-07-01"]
        else:
            result = df
    except Exception as e:
        result = pd.DataFrame({"error": [str(e)]})
    
    return query_text, sql_query, result

def show_samples():
    return "\n".join(sample_queries)

with gr.Blocks() as demo:
    gr.Markdown("""
    # Voice-to-SQL AI (Single Word Query Samples)
    Say one keyword like "Alice" or "sales greater than 100" to test quick filtering.
    """)
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Voice Input")            
            sample_btn = gr.Button("Show Sample Queries")            
            sample_output = gr.Textbox(label="Sample Queries", interactive=False)
        with gr.Column():
            text_output = gr.Textbox(label="Recognized Query", interactive=False)
            sql_output = gr.Textbox(label="Generated SQL", interactive=False)
            result_output = gr.Dataframe(label="Query Result")            
    
    sample_btn.click(show_samples, inputs=None, outputs=sample_output)
    audio_input.change(voice_to_sql, inputs=audio_input, outputs=[text_output, sql_output, result_output])

demo.launch()
