import streamlit as st
import ollama

def load_models():
    st.session_state.available_models = ollama.list()['models']

def find_model_index(selected_model):
    if selected_model is None:
        return 0
    for i, model in enumerate(st.session_state.available_models):
        if model.digest == selected_model.digest:
            return i
    return 0

if 'available_models' not in st.session_state:
    load_models()

if 'selected_model' not in st.session_state:
    loaded_models = ollama.ps()['models']
    if loaded_models:
        st.session_state.selected_model = loaded_models[0]
    else:
        st.session_state.selected_model = None

col1, col2 = st.columns(2)

index = find_model_index(st.session_state.selected_model)

with col1:
    selected_model = st.sidebar.selectbox(
        "Select the model to use",
        st.session_state.available_models,
        index=index,
        format_func=lambda model: model.model
    )
    st.session_state.selected_model = selected_model

with col2:
    if st.sidebar.button(icon=":material/autorenew:", label=''):
        load_models()

if st.session_state.selected_model:
    st.sidebar.markdown("### Model details")
    details = st.session_state.selected_model.get('details', None)
    if details:
        ddict = {}
        if 'parameter_size' in details:
            ddict['Size'] = details['parameter_size']
        if 'quantization_level' in details:
            ddict['Quant'] = details['quantization_level']
        if 'family' in details:
            ddict['Family'] = details['family']
        st.sidebar.write(ddict)

st.title("Ollama Chat Frontend")
st.caption("This is a simple chat frontend for the Ollama chatbot.")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    st.chat_message(message["role"]).write(message["content"])

def get_ollama_response():
    full_response = ''
    response = ollama.chat(
        model=st.session_state.selected_model.model,
        messages=st.session_state.chat_history,
        stream=True
    )
    for chunk in response:
        text = chunk['message']['content']
        full_response += text
        yield text
    st.session_state.chat_history.append({"role": 'assistant', "content": full_response})


def add_message(role, message):
    st.session_state.chat_history.append({"role": role, "content": message})

if prompt := st.chat_input():
    add_message('user', prompt)
    st.chat_message('user').write(prompt)
    st.chat_message('assistant').write(get_ollama_response())
