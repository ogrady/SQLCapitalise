from src import prettyprint

def main():
    print(prettyprint.pprint('SELECT * from mytable as mt WHERE 1=1 OR mt.x < 2 '))

if __name__ == "__main__":
    main()