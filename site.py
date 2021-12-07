import streamlit as st
import pickle
import pandas as pd
import random
import nltk
from nltk import word_tokenize
tk = nltk.WordPunctTokenizer()
from PIL import Image


hide_menu_style  = """
            <style>
            #MainMenu {visibility: hidden; }
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_menu_style, unsafe_allow_html=True)

descriptions = pickle.load( open( "descriptions.p", "rb" ) )
pokedex = pd.read_csv("pokemonNetwork.csv")

def build_model(source, state_size):
    model = {}
    for i in range(state_size, len(source)):
        current_word = source[i]
        previous_words = ' '.join(source[i-state_size:i])
        if previous_words in model:
            model[previous_words].append(current_word)
        else:
            model[previous_words] = [current_word]

    return model

def generate_text(model, state_size, min_length):
    def get_new_starter():
        return random.choice([s.split(' ') for s in model.keys() if s[0].isupper()])
    text = get_new_starter()

    i = state_size
    while True:
        key = ' '.join(text[i-state_size:i])
        if key not in model:
            text += get_new_starter()
            i += 1
            continue

        next_word = random.choice(model[key])
        text.append(next_word)
        i += 1
        if i > min_length and text[-1][-1] == '.':
            break
    return ' '.join(text)

pkmn = pokedex['Pokemon Name'].tolist()
name_tokens = []
for name in pkmn:
    name_tokens.append(list(name))
nt = nltk.Text(sum(name_tokens, []))

def generate_pkmn_name():
    state_size1 = 2
    min_length1 = 100
    poe1 = build_model(nt, state_size1)
    text1 = generate_text(poe1, state_size1, min_length1)
    text2 = text1[:random.randint(10, 20)]
    return text2.replace(' ', '').lower().capitalize()

def update(typee):
    tokens = tk.tokenize(descriptions[typee])
    new_name = generate_pkmn_name()

    for name in pkmn:
        tokens = [new_name if x == name else x for x in tokens]
    full_text = nltk.Text(tokens)

    state_size = 2
    min_length = 100
    model = build_model(full_text, state_size)
    text = generate_text(model, state_size, min_length)

    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace(" ' ", "'")
    text = text.replace(' - ', '-')
    return new_name, text

col1, col2, col3 = st.columns([3,2,8])


genre = col1.radio(
     "Choose your type:",
     ('Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water'))


button = col1.button('Create your pokemon!')

if button:
    name, text = update(genre)
    col3.markdown("<ins>**Name**</ins>", unsafe_allow_html=True)
    col3.markdown(f'<h1 style="text-align: center; color: white;">{name}</h1>', unsafe_allow_html=True)
    col3.markdown('&nbsp; ')
    col3.markdown("<ins>**Type**</ins>", unsafe_allow_html=True)
    if genre == 'Fairy':
        col3.image(Image.open(f'{genre}.png'))
    else:
        col3.image(Image.open(f'{genre}.gif'))
    col3.markdown("<ins>**Biology**</ins>", unsafe_allow_html=True)
    text2 = text.replace(name, f'***{name}***')
    col3.write(text2)


