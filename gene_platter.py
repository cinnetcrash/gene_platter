# gene_platter.py
# Interactive multi-gene time-series visualization tool for accessory/core genes
# Author: Dr Gültekin Ünal

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import re
from collections import defaultdict
import argparse
import os
import plotly.express as px

# Function to parse the .tab file and create a year-by-gene matrix
def parse_tab_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    genes_info = []
    current_gene = None
    current_variation = None
    current_taxa = []

    for line in lines:
        line = line.strip()
        if line.startswith('FT') and 'variation' in line:
            if current_gene and current_taxa:
                genes_info.append({
                    'gene': current_gene,
                    'variation': current_variation,
                    'taxa': current_taxa
                })
            current_variation = re.findall(r'\d+', line)[0] if re.findall(r'\d+', line) else None
            current_gene = None
            current_taxa = []
        elif '/gene=' in line:
            current_gene = line.split('=')[1].strip('"')
        elif '/taxa=' in line:
            taxa_list = line.split('=')[1].strip('"').split(' ')
            current_taxa = taxa_list

    if current_gene and current_taxa:
        genes_info.append({
            'gene': current_gene,
            'variation': current_variation,
            'taxa': current_taxa
        })

    gene_year_counts = defaultdict(lambda: defaultdict(int))
    for entry in genes_info:
        gene = entry['gene']
        for isolate in entry['taxa']:
            match = re.match(r'(\d{4})_', isolate)
            if match:
                year = match.group(1)
                gene_year_counts[gene][year] += 1

    gene_year_df = pd.DataFrame(gene_year_counts).fillna(0).astype(int)
    gene_year_df = gene_year_df.sort_index()
    return gene_year_df

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Interactive visualization of accessory/core genes over years.')
    parser.add_argument('-i', '--input', required=True, help='Input .tab file containing gene data')
    parser.add_argument('-o', '--output', required=True, help='Output folder for temporary files')
    args = parser.parse_args()

    # Check input file
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        exit(1)

    # Create output folder if missing
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    return args.input, args.output

# Main function
def main():
    input_file, output_folder = parse_arguments()

    # Parse the .tab file
    df = parse_tab_file(input_file)

    # Save processed matrix for reference
    matrix_path = os.path.join(output_folder, 'gene_year_matrix.csv')
    df.to_csv(matrix_path)

    # Start Dash app
    app = dash.Dash(__name__)
    server = app.server

    app.layout = html.Div([
        html.H1("Accessory/Core Genes - Yearly Trends", style={'textAlign': 'center'}),

        dcc.Dropdown(
            id='gene-dropdown',
            options=[{'label': gene, 'value': gene} for gene in df.columns],
            value=[df.columns[0]],  # Default selection
            multi=True,
            placeholder="Select one or more genes...",
            style={'width': '70%', 'margin': 'auto'}
        ),

        dcc.Graph(id='yearly-gene-graph', config={'toImageButtonOptions': {
            'format': 'png', # Format: png
            'filename': 'selected_genes_trend',
            'height': 600,
            'width': 1000,
            'scale': 2
        }})
    ])

    @app.callback(
        Output('yearly-gene-graph', 'figure'),
        Input('gene-dropdown', 'value')
    )
    def update_graph(selected_genes):
        if not isinstance(selected_genes, list):
            selected_genes = [selected_genes]

        # Melt the dataframe to plot multiple genes
        melted_df = df[selected_genes].reset_index().melt(id_vars='index', var_name='Gene', value_name='Isolate Count')
        melted_df.rename(columns={'index': 'Year'}, inplace=True)

        fig = px.line(
            melted_df,
            x='Year',
            y='Isolate Count',
            color='Gene',
            markers=True,
            title='Yearly Trends of Selected Genes'
        )
        fig.update_layout(xaxis_tickformat='%Y')
        return fig

    app.run_server(debug=True)

if __name__ == '__main__':
    main()
