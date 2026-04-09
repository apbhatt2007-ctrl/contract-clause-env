import sys

def main():
    with open('inference.py', 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('score=0.0,', 'score=1e-6,')
    content = content.replace('score=0.0)', 'score=1e-6)')
    content = content.replace('"score": 0.0,', '"score": 1e-6,')
    content = content.replace("'score': 0.0,", "'score': 1e-6,")
    content = content.replace("score: float = 0.0", "score: float = 1e-6")
    
    with open('inference.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
