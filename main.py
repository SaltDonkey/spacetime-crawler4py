import shelve

if __name__ == "__main__":
    with shelve.open("frontier.shelve") as shelf:
        print(shelf)