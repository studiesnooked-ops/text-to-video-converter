#!/usr/bin/env python3
import json
import click
import sys
from pathlib import Path
from src.m3u8_downloader import M3U8Downloader
from src.pdf_extractor import PDFExtractor
from src.text_to_video import TextToVideo

@click.group()
def cli():
    """Text-to-Video Converter CLI"""
    pass

@cli.command()
@click.option('--url', required=True, help='M3U8 playlist URL')
@click.option('--output', default='output/video.mp4', help='Output video file')
def download_m3u8(url, output):
    """Download video from M3U8 playlist"""
    try:
        downloader = M3U8Downloader()
        downloader.download(url, output)
        click.echo(f"✅ Video saved to: {output}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--pdf', required=True, help='PDF file path or URL')
@click.option('--output', default='output/extracted.txt', help='Output text file')
def extract_pdf(pdf, output):
    """Extract text content from PDF"""
    try:
        extractor = PDFExtractor()
        content = extractor.extract(pdf)
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            f.write(content)
        click.echo(f"✅ Content extracted to: {output}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--text', required=True, help='Text file path')
@click.option('--output', default='output/video.mp4', help='Output video file')
def convert_text_to_video(text, output):
    """Convert text file to video"""
    try:
        converter = TextToVideo()
        converter.convert(text, output)
        click.echo(f"✅ Video created: {output}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--config', required=True, help='JSON config file path')
def pipeline(config):
    """Run complete pipeline"""
    try:
        with open(config, 'r') as f:
            cfg = json.load(f)
        
        if 'm3u8_url' in cfg:
            click.echo("📹 Downloading M3U8 video...")
            downloader = M3U8Downloader()
            video_output = cfg.get('video_output', 'output/video.mp4')
            downloader.download(cfg['m3u8_url'], video_output)
        
        if 'pdf_url' in cfg:
            click.echo("📄 Extracting PDF...")
            extractor = PDFExtractor()
            pdf_output = cfg.get('pdf_output', 'output/extracted.txt')
            content = extractor.extract(cfg['pdf_url'])
            with open(pdf_output, 'w', encoding='utf-8') as f:
                f.write(content)
        
        click.echo("🎉 Pipeline completed!")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
