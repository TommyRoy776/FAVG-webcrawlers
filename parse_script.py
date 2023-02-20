import praw
from prawcore import NotFound
from pyChatGPT import ChatGPT
import tkinter as tk
from tkinter import messagebox
import time
# Import os module to manipulate file paths
import os
from datetime import datetime


# ------GUI Settings------
# Define a function to update the progress
def update_progress(progress, total_articles):
    popup_label.config(text=f"Processing {progress} out of {total_articles} articles. \n The script {progress} is "
                            f"generating..........\n Don't close any windows.")
    popup.update()


# ------Praw reddit Settings------
def sub_exists(reddit_obj, sub):
    exists = True
    try:
        reddit_obj.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists


def get_articles(reddit_obj, subreddit_name, attribute, number_of_articles):
    subreddit = reddit_obj.subreddit(subreddit_name)

    if attribute == "hot":
        articles = subreddit.hot(limit=number_of_articles)
    elif attribute == "news":
        articles = subreddit.news(limit=number_of_articles)
    elif attribute == "top":
        articles = subreddit.top(limit=number_of_articles)
    elif attribute == "rising":
        articles = subreddit.rising(limit=number_of_articles)
    else:
        print("Invalid attribute selection")
        return
    return articles


if __name__ == '__main__':

    # reddit authentication
    client_id = ""
    client_secret = ""
    user_agent = ""

    # create a reddit object
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent)

    check_target_subreddit = False
    check_article_attribute = False
    check_num_of_article = False
    while not check_target_subreddit:
        target_subreddit = str(input('Enter subreddit name: '))
        if not sub_exists(reddit, target_subreddit):
            print("Subreddit does not exist")
        else:
            check_target_subreddit = True

    while not check_article_attribute:
        article_attribute = str(input('Enter article attribute: hot, news, top, rising: '))
        if article_attribute not in ['hot', 'news', 'top', 'rising']:
            print("Invalid attribute selection")
        else:
            check_article_attribute = True

    while not check_num_of_article:
        num_of_article = input('Enter number of articles: ')
        if not num_of_article.isdigit() or int(num_of_article) < 0 or int(num_of_article) > 10:
            print("Please enter a number between 0 and 10")
        else:
            num_of_article = int(num_of_article)
            check_num_of_article = True

    # Create the main window
    popup = tk.Tk()
    popup.title("Information")

    # Make the window jump above all
    popup.attributes('-topmost', True)
    # stay in the middle of screen
    popup.eval('tk::PlaceWindow . center')

    # Set custom width and height for popup message
    popup_width = 340
    popup_height = 100

    # Set custom font and size for popup message
    popup_font = ('Segoe UI', 12)
    popup.geometry(
        f"{popup_width}x{popup_height}+{int(popup.winfo_screenwidth() / 2 - popup_width / 2)}+{int(popup.winfo_screenheight() / 2 - popup_height / 2)}")
    popup.resizable(False, False)

    # Create a label to display the progress
    popup_label = tk.Label(popup, text=f"You have {num_of_article} article(s) waiting to be processed. \n Opening "
                                       f"ChatGPT..... \n Don't close any windows.", font=popup_font, justify="center")
    popup_label.pack(pady=num_of_article)
    popup.update()

    # chatCPT authentication
    session_cookies = ""
    api = ChatGPT(session_cookies)

    # parse the reddit
    # change the text in .subreddit('target_Subreddit') to parse info from the target subreddit
    # change .hot .news .rising .top to access .hot .news .rising .top articles
    # change limit number for the desired number of articles.
    parse_articles = get_articles(reddit, target_subreddit, article_attribute, num_of_article)

    # Get the current date and time
    now = datetime.now()
    # Format the date and time as a string
    date_time_str = now.strftime("%m/%d/%Y %H:%M:%S")

    counter = 0

    for submission in parse_articles:
        # if content of the articles are not link, video, or empty, then return parse info
        if submission.selftext != '':

            # Specify the directory path where you want to store the file
            script_dir_path = "scripts"

            # Generate a script
            script_content = f"Create a storytelling script for a podcast episode based on the title and content below" \
                             f"Title: {submission.title}" \
                             f"Content: {submission.selftext}"

            # update and display current processing article num in pop up message box
            update_progress(counter + 1, num_of_article)

            # send the format_content to chatgpt_api (via chromeDriver)
            try:
                script_res = api.send_message(script_content)

            except Exception as e:
                print(f"Error: {e}.")
                if str(e).find("Too many requests in 1 hour. Try again later.") >= 0:
                    time.sleep(5 * 60)
                else:
                    api.driver.quit()
                    time.sleep(5)
                    api = ChatGPT(session_cookies)

            # increment the counter since an article is finished processing
            counter += 1
            # Specify the filename and file path where you want to store the file
            script_file_path = os.path.join(script_dir_path, f"{counter}-script-{submission.title}.txt")
            # Open file for writing (will create file if it doesn't exist)
            with open(script_file_path, "a") as file:
                # Write some text to the file
                file.write(f"Time: {date_time_str}")
                file.write(f"$$ {counter}. Title: {submission.title} $$")
                file.write("\n")
                file.write(script_res['message'])
                file.write("----------------------------------------------------------------\n")
                file.write("\n")

            # Time break to let chatCPT process the next article
            time.sleep(2)

            # Specify the directory path where you want to store the file
            tags_dir_path = "tags"

            # Generate a script
            tags_content = f"Create a list of tags for stable diffusion based on the title and content below" \
                           f"Title: {submission.title}" \
                           f"Content: {submission.selftext}"

            # send the format_content to chatgpt_api (via chromeDriver)
            try:
                tags_res = api.send_message(tags_content)

            except Exception as e:
                print(f"Error: {e}.")
                if str(e).find("Too many requests in 1 hour. Try again later.") >= 0:
                    time.sleep(5 * 60)
                else:
                    api.driver.quit()
                    time.sleep(5)
                    api = ChatGPT(session_cookies)

            # Specify the filename and file path where you want to store the file
            tags_file_path = os.path.join(tags_dir_path, f"{counter}-tags-{submission.title}.txt")
            # Open file for writing (will create file if it doesn't exist)
            with open(tags_file_path, "a") as file:
                # Write some text to the file
                file.write(f"Time: {date_time_str}")
                file.write(f"$$ {counter}. Title: {submission.title} $$")
                file.write("\n")
                file.write(tags_res['message'])
                file.write("----------------------------------------------------------------\n")
                file.write("\n")

    # Create a pop-up message box when the processing is complete
    messagebox.showinfo(title="Information",
                        message=f"You have generated {counter} script(s). Press OK to go back to the "
                                f"program.")
    # close the pop-up box
    popup.destroy()
