import pickle
import random
from googletrans import Translator

f = open('./data/happy_episodes_add_image_url_list.bin', 'rb')
happy_episodes = pickle.load(f)
f.close()

translator = Translator()

happy_episode = random.choice(happy_episodes)

trans_en = translator.detect(happy_episode['content'])

print(type(trans_en))
print(trans_en.lang)
