from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import pairwise_distances_argmin_min

model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')

def find_closest_words(input_data, word_data, n=5):
    input_embeddings = model.encode(input_data) 

    word_embeddings = model.encode([word['word'] for word in word_data])  
    closest_words = []

    similarities = cosine_similarity(input_embeddings, word_embeddings) 

    for sim_row in similarities:
        closest_indices = sim_row.argsort()[-n:] 
        for idx in closest_indices:
            closest_words.append(word_data[idx])

    # 중복 제거
    unique_words = [dict(t) for t in {tuple(d.items()) for d in closest_words}]

    return unique_words



def find_farthest_words(input_data, word_data, n=3):
    input_embeddings = model.encode(input_data)  # 입력 데이터를 임베딩

    word_embeddings = model.encode([word['word'] for word in word_data])  # 단어 데이터를 임베딩
    farthest_words = []

    for input_emb in input_embeddings:
        distances = cosine_similarity([input_emb], word_embeddings)  # 코사인 유사도 계산
        farthest_indices = distances.argsort()[0][:n]  # 상위 n개 거리(거리가 먼 단어) 인덱스 추출

        for idx in farthest_indices:
            farthest_words.append(word_data[idx])
            
    unique_words = [dict(t) for t in {tuple(d.items()) for d in farthest_words}]

    return unique_words



def find_most_similar_news(input_keywords, news_data, n=3):
    # 입력 데이터를 임베딩
    input_embedding = model.encode(' '.join(input_keywords))

    # 뉴스 데이터를 임베딩
    news_embeddings = [model.encode(' '.join(news['특성추출'])) for news in news_data]

    # 입력 데이터와 뉴스 데이터 간의 코사인 유사도 계산
    similarities = cosine_similarity([input_embedding], news_embeddings)
    most_similar_indices = similarities.argsort()[0][::-1][:n]  # 상위 n개 유사도 인덱스 추출

    most_similar_news = [news_data[idx] for idx in most_similar_indices]

    return most_similar_news


def combine_text(news):
    # '특성추출', '본문', '통합분류' 키의 값을 결합
    combined_text = ''

    if '특성추출' in news:
        combined_text += ' '.join(news['특성추출']) + ' '

    if '본문' in news:
        combined_text += news['본문'] + ' '

    if '통합 분류1' in news:
        combined_text += ' '.join(news['통합 분류1']) + ' '

    if '통합 분류2' in news:
        combined_text += ' '.join(news['통합 분류2']) + ' '

    if '통합 분류3' in news:
        combined_text += ' '.join(news['통합 분류3']) + ' '

    return combined_text

def find_most_similar_news(input_keywords, news_data, n=10):
    # 입력 데이터를 하나의 텍스트로 결합
    input_text = ' '.join(input_keywords)

    # 각 뉴스 데이터를 하나의 텍스트로 결합하여 임베딩
    news_texts = [combine_text(news) for news in news_data]

    # 입력 데이터와 뉴스 데이터 간의 코사인 유사도 계산
    input_embedding = model.encode(input_text)
    news_embeddings = model.encode(news_texts)
    similarities = cosine_similarity([input_embedding], news_embeddings)
    most_similar_indices = similarities.argsort()[0][::-1][:n]  # 상위 n개 유사도 인덱스 추출

    most_similar_news = [news_data[idx] for idx in most_similar_indices]

    # 중복 제거
    unique_news = []
    seen_indices = set()
    for news in most_similar_news:
        news_index = news_data.index(news)
        if news_index not in seen_indices:
            unique_news.append(news)
            seen_indices.add(news_index)

    return unique_news


def find_most_dissimilar_news(input_keywords, news_data, n=3):
    input_text = ' '.join(input_keywords)

    news_texts = [combine_text(news) for news in news_data]

    input_embedding = model.encode(input_text)
    news_embeddings = model.encode(news_texts)
    # distances = pairwise_distances_argmin_min(input_embedding.reshape(1, -1), news_embeddings, metric='cosine')
    similarities = cosine_similarity([input_embedding], news_embeddings)
    furthest_indices = similarities.argsort()[0][:n]
    # furthest_indices = distances[0].argsort()[-n:][::-1]  # 상위 n개 거리가 먼 인덱스 추출

    furthest_news = [news_data[idx] for idx in furthest_indices]

    # 중복 제거
    unique_furthest_news = []
    seen_indices = set()
    for news in furthest_news:
        news_index = news_data.index(news)
        if news_index not in seen_indices:
            unique_furthest_news.append(news)
            seen_indices.add(news_index)

    return unique_furthest_news
