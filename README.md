# Learning the Unseen: Data-Augmented Deep Learning for PTM Discovery with Prosit-PTM

Code accompanying Gabriel *et al.*, "Learning the Unseen: Data-Augmented Deep Learning for PTM Discovery with Prosit-PTM".

- `figures/`: one Jupyter notebook per figure that redraws every data panel of Figs. 1–6 and Extended Data Figs. 1–10 from the
  deposited source data.
- `analysis/`: analysis notebooks for the HLA motif / latent-space UMAP analysis and the preparation of the amino-acid
  substitution augmentation data.

## Source data

The source data are deposited on figshare: https://doi.org/10.6084/m9.figshare.34601982

| file | content |
|---|---|
| `Wilhelm_SourceData.xlsx` | one worksheet per figure panel; the `README` worksheet lists every panel and its data file(s) |
| `Wilhelm_SourceData_<panel>.parquet` | per-point data of distribution panels (violin and box plots, precision–recall and FLR curves, density and scatter plots) |
| `Wilhelm_SourceData_<panel>*.csv` | n, medians and box statistics of these panels |
| `README.md` | description of every file and column |

## Reproducing the figures

```bash
conda env create -f environment.yml
conda activate prosit-ptm-figures
cd figures
jupyter notebook
```

Open a notebook (`Fig1.ipynb` … `Fig6.ipynb`, `ED_Fig1.ipynb` … `ED_Fig10.ipynb`) and run all cells. The data are loaded with
`figures/source_data.py`:

- By default the files are downloaded from the figshare record (article 34601982) into `figures/data/` on first use.
- To use a local copy of the record, set `SOURCE_DATA_DIR` to the folder containing the downloaded files.

```python
from source_data import fetch, table, readme

table('Fig1a')                      # worksheet of a panel
table('Fig4e_totals')               # second table of the Fig4e worksheet
table('ED_Fig6a_summary')           # summary CSV of a panel
fetch('Wilhelm_SourceData_Fig1e.parquet')  # local path of a per-point file
readme('ED_Fig8')                   # panels and files of one figure
```

Panels are written as PDF and PNG to `figures/regenerated_panels/<figure>/`. Schematic panels without data are not included.

## Analysis notebooks

| notebook | content |
|---|---|
| `analysis/HLA_motif_umap_pipeline.ipynb` | UMAP embeddings of Prosit-PTM latent representations of amino acids and modified residues, HDBSCAN / agglomerative clustering, position-specific enrichment and sequence logos of HLA class I alleles (Extended Data Fig. 8) |
| `analysis/PTMs_Augmentation.ipynb` | merging of peptide sequences with amino-acid substitutions and train / validation / hold-out splits by iterative stratification for the augmentation training data |

Input paths are set in the configuration cell of each notebook (`<PATH_...>` placeholders). Additional packages are needed for
these notebooks: tensorflow, umap-learn, hdbscan, scikit-learn, biopython, logomaker, adjustText, joblib, tqdm,
spectrum_fundamentals and iterative-stratification.

## Related resources

- Mass spectrometry raw data and search results: ProteomeXchange / PRIDE PXD070416, PXD070496, PXD070858, PXD070864,
  PXD070537, PXD070866
- Models: Prosit-22PTM (https://zenodo.org/records/17641433), Prosit-40PTM (https://zenodo.org/records/17641485);
  available for inference through Koina (https://github.com/wilhelm-lab/koina)
- Training data: https://huggingface.co/datasets/Wilhelmlab/prospect-ptms-irt and
  https://huggingface.co/datasets/Wilhelmlab/prospect-ptms-ms2
- Data processing: https://github.com/wilhelm-lab/PROSPECT
- Model training: https://github.com/wilhelm-lab/dlomix
- Rescoring: https://github.com/wilhelm-lab/oktoberfest

## Citation

Gabriel W, Zolg DP, Giurcoiu V, *et al.* Learning the Unseen: Data-Augmented Deep Learning for PTM Discovery with Prosit-PTM. https://www.biorxiv.org/content/10.1101/2025.11.07.687302v2

## License

MIT, see `LICENSE`.
