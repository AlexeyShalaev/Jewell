from dataclasses import dataclass
import math


@dataclass
class Document:
    id: str
    relevance: float


@dataclass
class QueryWord:
    data: str
    is_minus: bool
    is_stop: bool


@dataclass
class Query:
    plus_words: set
    minus_words: set


class SearchEngine:
    MAX_RESULT_DOCUMENT_COUNT: int
    _stop_words: set
    _word_to_document_freqs: dict
    _documents: set

    def __init__(self, max_result_document_count: int = 5):
        self.MAX_RESULT_DOCUMENT_COUNT = max_result_document_count
        self._stop_words = set()
        self._word_to_document_freqs = dict()
        self._documents = set()

    # public methods
    def set_stop_words(self, text: str):
        self._stop_words = set(text.split())

    def add_document(self, document_id: str, document: str):
        document = document.lower()
        words = self.__split_into_words_no_stop(document)
        inv_word_count = 1 / len(words)
        for word in words:
            if word not in self._word_to_document_freqs.keys():
                self._word_to_document_freqs[word] = dict()
            if document_id in self._word_to_document_freqs[word].keys():
                self._word_to_document_freqs[word][document_id] += inv_word_count
            else:
                self._word_to_document_freqs[word][document_id] = inv_word_count
        self._documents.add(document_id)

    def find_top_documents(self, raw_query: str):
        raw_query = raw_query.lower()
        query = self.__parse_query(raw_query)
        matched_documents = self.__find_all_documents(query)
        matched_documents.sort(key=lambda x: x.relevance, reverse=True)
        if len(matched_documents) > self.MAX_RESULT_DOCUMENT_COUNT:
            return matched_documents[:self.MAX_RESULT_DOCUMENT_COUNT]
        return matched_documents

    def get_document_count(self):
        return len(self._documents)

    def match_document(self, raw_query: str, document_id: str):
        query = self.__parse_query(raw_query)
        matched_words = list()
        for word in query.plus_words:
            for key in self._word_to_document_freqs.keys():
                if word in key:
                    if document_id in self._word_to_document_freqs[key].keys():
                        matched_words.append(word)
                    break
        for word in query.minus_words:
            if word in self._word_to_document_freqs.keys():
                if document_id in self._word_to_document_freqs[word].keys():
                    matched_words.clear()
        return matched_words

        # private methods

    def __is_stop_word(self, word: str) -> bool:
        return word in self._stop_words

    def __split_into_words_no_stop(self, text: str) -> list:
        return [word for word in text.split() if not self.__is_stop_word(word)]

    def __parse_query_word(self, text: str) -> QueryWord:
        is_minus = False
        if text[0] == '-':
            is_minus = True
            text = text[1:]
        return QueryWord(text, is_minus, self.__is_stop_word(text))

    def __parse_query(self, text: str) -> Query:
        query = Query(set(), set())
        for word in text.split():
            query_word = self.__parse_query_word(word)
            if not query_word.is_stop:
                if query_word.is_minus:
                    query.minus_words.add(query_word.data)
                else:
                    query.plus_words.add(query_word.data)
        return query

    def __compute_word_inverse_document_freq(self, word: str) -> float:
        if word in self._word_to_document_freqs.keys():
            return math.log(self.get_document_count() / len(self._word_to_document_freqs[word]))
        else:
            for key in self._word_to_document_freqs.keys():
                if word in key:
                    return math.log(self.get_document_count() / len(self._word_to_document_freqs[key]))

    def __find_all_documents(self, query: Query) -> list:
        document_to_relevance = dict()
        for word in query.plus_words:
            if word in self._word_to_document_freqs.keys():
                inverse_document_freq = self.__compute_word_inverse_document_freq(word)
                for document_id, term_freq in self._word_to_document_freqs[word].items():
                    if document_id in document_to_relevance.keys():
                        document_to_relevance[document_id] += term_freq * inverse_document_freq
                    else:
                        document_to_relevance[document_id] = term_freq * inverse_document_freq
            else:
                for key in self._word_to_document_freqs.keys():
                    if word in key:
                        inverse_document_freq = self.__compute_word_inverse_document_freq(word)
                        for document_id, term_freq in self._word_to_document_freqs[key].items():
                            if document_id in document_to_relevance.keys():
                                document_to_relevance[document_id] += term_freq * inverse_document_freq * 0.8
                            else:
                                document_to_relevance[document_id] = term_freq * inverse_document_freq * 0.8
                        break

        for word in query.minus_words:
            if word in self._word_to_document_freqs.keys():
                for document_id in self._word_to_document_freqs[word].keys():
                    del self._word_to_document_freqs[word][document_id]
        matched_documents = list()
        for document_id, relevance in document_to_relevance.items():
            matched_documents.append(Document(document_id, relevance))
        return matched_documents


def print_document(document: Document):
    print(f"id = {document.id}, relevance = {document.relevance}")


def search_documents(documents: list, query: str, max_result_document_count: int = 5) -> list:
    result = list()
    if max_result_document_count < 0:
        max_result_document_count = len(documents)
    search_engine = SearchEngine(max_result_document_count)
    for document in documents:
        search_engine.add_document(document['id'], document['data'])
    for document in search_engine.find_top_documents(query):
        result.append(document.id)
    del search_engine
    return result
