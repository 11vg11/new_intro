run:
	python3 scripts/run_profile.py

photo:
	python3 scripts/run_profile.py --skip-heatmap --skip-info

clean:
	rm -f source-prepped.png source-prepped.png.sha256 output/contrib-heatmap.svg output/avi-ascii.svg output/info-card.svg
