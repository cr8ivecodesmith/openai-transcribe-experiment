import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

# Prefer stdlib tomllib (Python 3.11+); fall back to 'toml' if available
try:
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - runtime fallback
    tomllib = None  # type: ignore
    try:
        import toml  # type: ignore
    except Exception:
        toml = None  # type: ignore


PROJECT_DIR = Path(__file__).parent
PROJECT_ENV = PROJECT_DIR.joinpath('.env')
ARTICLES_TOML = PROJECT_DIR.joinpath('articles.toml')


def _load_env_and_client() -> OpenAI:
    """Load environment variables and initialize OpenAI client."""
    load_dotenv(PROJECT_ENV)
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set. Add it to .env')
    return OpenAI(api_key=api_key)


def _load_articles_config(config_path: Path = ARTICLES_TOML) -> Dict[str, Any]:
    """Load article type configuration from TOML.

    The TOML file should have top-level tables keyed by article type. Each
    table should include at minimum a 'prompt' string. Optional fields like
    'model' can override the default model used.
    """
    if not config_path.exists():
        raise FileNotFoundError(f'Config not found: {config_path}')

    data: Dict[str, Any]
    if tomllib is not None:
        with config_path.open('rb') as fh:  # tomllib expects bytes
            data = tomllib.load(fh)  # type: ignore[arg-type]
    elif 'toml' in globals() and toml is not None:  # type: ignore[name-defined]
        with config_path.open('r', encoding='utf-8') as fh:
            data = toml.load(fh)  # type: ignore[assignment]
    else:
        raise RuntimeError(
            'No TOML parser available. Use Python 3.11+ or install "toml".')

    return data


def _read_transcript(transcript_path: Path) -> str:
    """Read transcript text from a file."""
    if not transcript_path.exists():
        raise FileNotFoundError(f'Transcript not found: {transcript_path}')
    return transcript_path.read_text(encoding='utf-8')


def _build_prompt(base_prompt: str, transcript_text: str) -> str:
    """Interpolate transcript into prompt template.

    If the template contains '{transcript}', substitute it. Otherwise, append
    the transcript to the end under a "Transcript:" header.
    """
    if '{transcript}' in base_prompt:
        return base_prompt.format(transcript=transcript_text)
    return f"{base_prompt.rstrip()}\n\nTranscript:\n{transcript_text}"


def _generate_article(client: OpenAI, prompt: str, model: str = 'gpt-4o-mini') -> str:
    """Generate article text from a prompt using OpenAI."""
    resp = client.responses.create(
        model=model,
        input=prompt,
    )
    # openai>=1.0 exposes output_text convenience property
    try:
        return resp.output_text  # type: ignore[attr-defined]
    except Exception:
        # Fallback: extract from first text output
        for item in getattr(resp, 'output', []) or []:
            if getattr(item, 'type', None) == 'output_text':
                return getattr(item, 'content', '')
        # Last resort: stringification
        return str(resp)


def _write_article(output_dir: Path, transcript_path: Path, article_type: str, content: str) -> Path:
    """Write generated article to the output directory as Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    outfile = output_dir.joinpath(f"{transcript_path.stem}_{article_type}.md")
    outfile.write_text(content, encoding='utf-8')
    return outfile


def main(args) -> None:
    article_type = args.ARTICLE_TYPE
    transcript_file = Path(args.TRANSCRIPT_FILE)

    client = _load_env_and_client()
    config = _load_articles_config()

    if article_type not in config:
        available = ', '.join(sorted(config.keys()))
        raise KeyError(
            f'Article type "{article_type}" not found in articles.toml. '
            f'Available types: {available}'
        )

    entry = config[article_type]
    if 'prompt' not in entry or not isinstance(entry['prompt'], str):
        raise ValueError(
            f'Invalid config for type "{article_type}": missing string "prompt"')

    model = entry.get('model') or 'gpt-4o-mini'
    base_prompt = entry['prompt']

    transcript_text = _read_transcript(transcript_file)
    prompt = _build_prompt(base_prompt, transcript_text)

    print(f'Generating article using type "{article_type}" and model "{model}"...')
    article_text = _generate_article(client, prompt, model=model)

    # Default output directory mirrors existing repo layout unless overridden
    output_dir = Path(args.output_dir) if getattr(args, 'output_dir', None) else PROJECT_DIR.joinpath('output')
    outfile = _write_article(output_dir, transcript_file, article_type, article_text)
    print(f'Article written to {outfile}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('ARTICLE_TYPE')
    parser.add_argument('TRANSCRIPT_FILE')
    parser.add_argument('-o', '--output-dir', dest='output_dir')

    params = parser.parse_args()
    main(params)
