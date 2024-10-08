import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from src.controller import  capasNeuronales
from src.utils import logger

# Se debe activar cada primera vez o cambio de maquina de pc o lugar donde se corre, luego se debe comentar
# nltk.download()  # despliega el menu
# nltk.download('punkt') 
# nltk.download('punkt_tab') 
    
def analyzingTextRN(chat_id, bot, frase):
    module = "redneuronal.analyzingText.FN."
        
    data = capasNeuronales()
    
    entradas = []
    salidas = []
    
    for row in data:
        ent = row["entrada"]
        sal = row["salida"]
        
        entradas.append(ent.lower())
        salidas.append(sal.lower())
    
    tokenizer = nltk.word_tokenize
    entradas_tokenizadas = [tokenizer(entrada) for entrada in entradas]
    
    vectorizer = CountVectorizer(tokenizer=tokenizer, token_pattern=None)
    X = vectorizer.fit_transform(entradas)
    
    modelo = MultinomialNB()
    modelo.fit(X, salidas)
    
    X_nueva = []
    
    try:
        X_nueva = vectorizer.transform([frase])
        prediccion = modelo.predict(X_nueva)[0]
        print ('  ************************************')
        print ('  **  RED NEURONAL PREDICCION       **')
        print ('  ************************************')
        print ('     Texto ingresado:')
        print (f"        {frase}")
        print ('     Prediccion realizada:')
        print (f"        {prediccion}")
        print ('  ************************************')
        # print(f"Predicción para '{frase}': {prediccion}")
        return prediccion
    except Exception as err:
        print("[X]", err)
        logger("ERROR", err, f"{module}59")
        