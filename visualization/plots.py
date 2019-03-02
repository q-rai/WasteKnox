from bokeh.plotting import figure, output_file, show
from bokeh.layouts import layout, column
from bokeh.models import ColumnDataSource

import intake

# CUSTOMIZATION
DIVERGENT_COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
LINE_PARAMS = {'line_width': 2}


def fetch_bokeh_sources(catalog_filename):
    """Define Bokeh Data Sources

    """
    catalog = intake.open_catalog(catalog_filename)
    return {
        'mulch': ColumnDataSource(catalog.solid_waste_mulch.read().pivot(index='Month', columns='Type'))
    }


def mulch_line_plot(sources):
    mulch_source = sources['mulch']

    color_iter = iter(DIVERGENT_COLORS)

    plot = figure(plot_width=1200, plot_height=400,
                  title="Tons of Leaves/Brush by Month", x_axis_type="datetime")

    plot.line(x='Month', y='Mulch_Brush', source=mulch_source,
              legend='Brush', color=next(color_iter), **LINE)
    plot.line(x='Month', y='Mulch_Leaves', source=mulch_source,
              legend='Leaves', color=next(color_iter), **params)

    plot.xaxis.axis_label = "Month"
    plot.yaxis.axis_label = "Tons"

    return plot


def main():
    catalog_filename = 'catalog.yml'
    sources = fetch_bokeh_sources(catalog_filename)

    output_file('visualization.html')

    plots = [
        mulch_line_plot(sources),
        [mulch_line_plot(sources), mulch_line_plot(sources)]
    ]

    show(layout(plots))


if __name__ == '__main__':
    main()
