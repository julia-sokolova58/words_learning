from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
import re
import random
import spacy
import yake
from gensim.models import KeyedVectors
from huggingface_hub import hf_hub_download
from collections import Counter


nlp = spacy.load("de_core_news_sm")


def find_snippet_in_book(book_path, first_five, last_five):
    with open(book_path, 'r', encoding='utf-8') as f:
        text = f.read()

    first_pos = text.find(first_five)
    if first_pos == -1:
        return None

    last_pos = text.find(last_five, first_pos)
    if last_pos == -1:
        return None

    return text[first_pos:last_pos + len(last_five)]


def read_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        file = f.read().replace("\n", " ").lower()
    text = re.sub(r"[^\w\s]", "", file)
    return text


def lemmatization(text):
    nlp = spacy.load("de_core_news_sm")
    spacy_text = nlp(text)
    no_sw = [token.text for token in spacy_text if not (token.is_stop or token.is_space)]
    filtered = nlp(" ".join(no_sw))
    lemmas_pos = []
    for token in filtered:
        lemmas_pos.append((token.lemma_.lower(), token.pos_))
    lemmas_pos_df = pd.DataFrame(lemmas_pos, columns=["lemma", "pos"])

    return lemmas_pos_df  


def diff_pos(lemmas_pos_df, pos):
    pos_df = lemmas_pos_df[lemmas_pos_df["pos"] == pos]
    return pos_df


def to_text(df):
    text = " ".join(token for token in df["lemma"])
    return text


def extract_kws(text):
    kw_extractor = yake.KeywordExtractor(lan="de",n=1, top=3, dedupLim=0.7, dedupFunc='seqm')
    keywords = pd.DataFrame(kw_extractor.extract_keywords(text))
    return list(keywords[0])


def extract_unique_kws(text, n_to_extract, n_result):
    kw_extractor = yake.KeywordExtractor(lan="de",n=1, top=n_to_extract, dedupLim=0.7,
                                         dedupFunc='seqm')
    keywords = list(pd.DataFrame(kw_extractor.extract_keywords(text))[0])

    total = len(keywords)
    start = int(total * 0.5)
    end = int(total * 0.7)
    mid_words = keywords[start:end]
    return random.sample(mid_words, min(n_result, len(mid_words)))


def final_wordlist(text):
    lemmas_pos_df = lemmatization(text)

    verbs_df = diff_pos(lemmas_pos_df, "VERB")
    nouns_df = diff_pos(lemmas_pos_df, "NOUN")

    verbs_text = to_text(verbs_df)
    nouns_text = to_text(nouns_df)

    key_verbs = extract_kws(verbs_text)
    key_nouns = extract_kws(nouns_text)

    unique_verbs = extract_unique_kws(verbs_text, 500, 3)
    unique_nouns = extract_unique_kws(nouns_text, 500, 3)

    result_verbs = key_verbs + unique_verbs
    result_nouns = key_nouns + unique_nouns
    result_nouns = [i.capitalize() for i in result_nouns]

    result_verbs = list(dict.fromkeys(result_verbs))
    result_nouns = list(dict.fromkeys(result_nouns))
    
    return result_verbs, result_nouns


model_path = hf_hub_download(
    repo_id="Word2vec/german_model",
    filename="german.model")
similarity_model = KeyedVectors.load_word2vec_format(
    model_path,
    binary=True,
    unicode_errors="ignore")


def related_words(word, n=3):
    similar_words = pd.DataFrame(similarity_model.most_similar(word, topn=n))[0]
    return list(similar_words)


def parse_noun_declension(word):

    link = f"https://www.verbformen.ru/sklonenie/sushhestvitelnye/{word.capitalize()}.htm"
    response = requests.get(link)
    if response.status_code == 404:
      return "Кажется, такого слова нет в нашей базе данных:("
    else:
      soup = BeautifulSoup(response.text, 'html.parser')
      
      word_cell = soup.find('td', string='der')
      if word_cell:
          base_word = word_cell.find_next('td').find('b').text
          base_form = f"der {base_word}"
      else:
          base_form = None
      
      part_of_speech = soup.find('span', title='существительное')
      part_of_speech = part_of_speech.text if part_of_speech else None
      
      gender = soup.find('span', title='мужской род')
      gender = gender.text if gender else None
      
      decl_type = soup.find('span', title='правильное склонение')
      decl_type = decl_type.text if decl_type else None
      
      endings = soup.find('span', title='родительный с -s, множественное с -e')
      endings = endings.text if endings else None
      
      gen_row = soup.find('th', string='Pод.')
      if gen_row:
          gen_cell = gen_row.find_next('td').find_next('td')
          gen_sing = gen_cell.text.strip()
      else:
          gen_sing = None
      
      nom_plural_row = soup.find('th', string='Им.')
      if nom_plural_row:
          rows = soup.find_all('tr')
          for row in rows:
              if row.find('th', string='Им.'):
                  plural_cell = row.find_all('td')[-1]
                  nom_plural = plural_cell.text.strip()
                  break
      else:
          nom_plural = None
      
      result = {'base_form': base_form, 'genitive_singular': gen_sing, 'nominative_plural': nom_plural,
                'part_of_speech': part_of_speech, 'gender': gender,'declension_type': decl_type, 
                'endings': endings}

      result_str = f"{result["base_form"]} ({result["gender"]} род)\nGenitiv SG: {result["genitive_singular"]}\nPlural: {result["nominative_plural"]}"


      return result_str



def parse_verb_page(word):

    link = f"https://www.verbformen.ru/sprjazhenie/{word}.htm"
    response = requests.get(link)
    if response.status_code == 404:
      return "Кажется, такого слова нет в нашей базе данных:("
    else:
      soup = BeautifulSoup(response.text, 'html.parser')
      result = {
          'infinitive': None,
          'present_3sg': None,
          'preterite_3sg': None,
          'participle': None,
          'auxiliary': None,
          'type': None,
          'level': None,
          'reflexive': None
      }
      
      vgrnd = soup.find('span', class_='vGrnd')
      if vgrnd:
          parts = []
          for b in vgrnd.find_all('b'):
              text = b.get_text(strip=True)
              if text:
                  parts.append(text)
          if parts:
              result['infinitive'] = ''.join(parts)
      
      stamm = soup.find('p', id='stammformen')
      if stamm:
          bold_tags = stamm.find_all('b')
          if len(bold_tags) == 3:
              result['present_3sg'] = bold_tags[0].get_text(strip=True)
              result['preterite_3sg'] = bold_tags[1].get_text(strip=True)
              result['participle'] = bold_tags[2].get_text(strip=True)

          if len(bold_tags) == 5:
              result['present_3sg'] = bold_tags[0].get_text(strip=True) + " " + bold_tags[1].get_text(strip=True)
              result['preterite_3sg'] = bold_tags[2].get_text(strip=True) + " " + bold_tags[3].get_text(strip=True)
              result['participle'] = bold_tags[4].get_text(strip=True)
          
          for elem in stamm.find_all():
              if elem.name == 'i' and elem.parent.name != 'b':
                  aux = elem.get_text(strip=True).lower()
                  if 'hat' in aux or 'haben' in aux:
                      result['auxiliary'] = 'haben'
                  elif 'ist' in aux or 'sein' in aux:
                      result['auxiliary'] = 'sein'
                  break
      
      rinf = soup.find('p', class_='rInf')
      if rinf:
          spans = rinf.find_all('span', title=True)
          for span in spans:
              title = span.get('title', '')
              text = span.get_text(strip=True)
              if 'неправильный' in title or 'правильный' in title:
                  result['type'] = text
              if 'Сертификат' in title:
                  result['level'] = text
          
          if 'sich' in rinf.get_text():
              result['reflexive'] = 'sich'
    
      result_str = f"{result["auxiliary"]}\nPräsens 3SG: {result["present_3sg"]},\nPräteritum 3SG: {result["preterite_3sg"]}"

    return result_str