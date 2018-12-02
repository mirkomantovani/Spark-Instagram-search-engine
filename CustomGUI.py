# Mirko Mantovani
import easygui as eg


def ask_query():
    msg = "Enter your query"
    title = "Query"
    response = eg.enterbox(msg, title)
    return response


def display_query_results(docs_list, query_tokens):
    # url_from_code = Crawler.get_url_from_code()
    msg = "Preprocessed query: "+str(query_tokens)+"\nThese are the results of your query, you can double click" \
                                                   " or select and press ok on a" \
                                                   " result to open the web page in a new tab of your default browser" \
                                                   " or you can choose to Show more results. Press cancel to go back" \
                                                   " to the main menu."
    title = "Query results"
    # print(url_from_code)
    url_list = [str(code[0])+' '+str(code[1]) for code in docs_list]
    url_list.append("Show more results")
    choice = eg.choicebox(msg, title, url_list)
    return choice
