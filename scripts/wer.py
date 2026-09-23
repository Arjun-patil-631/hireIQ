"""Calculate Whisper word error rate for a reference transcript and hypothesis transcript."""
import argparse
from pathlib import Path

from jiwer import wer


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--reference', required=True)
    p.add_argument('--hypothesis', required=True)
    args = p.parse_args()
    ref = Path(args.reference).read_text(encoding='utf-8').strip()
    hyp = Path(args.hypothesis).read_text(encoding='utf-8').strip()
    score = wer(ref, hyp)
    print(f'WER: {score:.2%}')


if __name__ == '__main__':
    main()
