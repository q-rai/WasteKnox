import datetime as dt

from bokeh.plotting import figure, output_file, curdoc
from bokeh.layouts import layout, column
from bokeh.models import ColumnDataSource, CDSView, IndexFilter
from bokeh.models.widgets import Panel, Tabs, DateRangeSlider, Div, RadioButtonGroup

import intake

# UNIT
UNIT_CONVERSION = {
    "Pounds": 1.0,
    "Metric Tons": 1 / 2204.62,
    "School Bus": 1 / 23500,
    "Space Shuttle": 1 / 150000,
    "Sunspheres": 1 / (600*2204.62),
}
UNIT_CONVERSION_MAP = list(UNIT_CONVERSION.keys())


# THEME
DIVERGENT_COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
LINE_PARAMS = {'line_width': 2}


# GLOBALS (TO MODIFY PLOTS/DIVS)
ELEMENT_CALLBACKS = []


def fetch_bokeh_sources(catalog_filename):
    """Define Bokeh Data Sources

    """
    catalog = intake.open_catalog(catalog_filename)
    dataframes = {
        'mulch_df': catalog.solid_waste_mulch.read().pivot(index='Month', columns='Type')
    }
    sources = {
        'mulch': ColumnDataSource(dataframes['mulch_df']),
    }
    return {'dataframes': dataframes, 'sources': sources}


def source_filters(sources):
    _state = {
        'date_range': (
            dt.datetime(year=2018, month=1, day=1),
            dt.datetime(year=2018, month=12, day=1)),
        'units': 0,
    }

    def _handle_state_filter():
        df = sources['dataframes']['mulch_df']
        df = df[(df.index >= _state['date_range'][0]) & (df.index <= _state['date_range'][1])]
        units = UNIT_CONVERSION_MAP[_state['units']]
        df = df * UNIT_CONVERSION[units]
        sources['sources']['mulch'].data = ColumnDataSource(df).data

        for callback in ELEMENT_CALLBACKS:
            callback(sources=sources, **_state)

    def _date_slider_handler(attr, old, new):
        start_time, end_time = new
        start_date = dt.datetime.fromtimestamp(start_time / 1000)
        end_date = dt.datetime.fromtimestamp(end_time / 1000)
        _state['date_range'] = (start_date, end_date)
        _handle_state_filter()

    start_date = dt.datetime(year=2018, month=12, day=1)
    end_date = dt.datetime(year=2018, month=12, day=1)
    date_slider = DateRangeSlider(start=_state['date_range'][0], end=_state['date_range'][1], value=_state['date_range'], step=1, title="Date Range")
    date_slider.on_change('value', _date_slider_handler)

    def _radio_button_group_handler(attr, old, new):
        _state['units'] = int(new)
        _handle_state_filter()

    radio_button_group = RadioButtonGroup(labels=UNIT_CONVERSION_MAP, active=0, width=600)

    radio_button_group.on_change('active', _radio_button_group_handler)

    return [date_slider, radio_button_group]


def mulch_line_plot(sources):
    mulch_source = sources['sources']['mulch']

    color_iter = iter(DIVERGENT_COLORS)

    plot = figure(plot_width=1200, plot_height=400,
                  title="Tons of Leaves/Brush by Month", x_axis_type="datetime")

    plot.line(x='Month', y='Mulch_Brush', source=mulch_source,
              legend='Brush', color=next(color_iter), **LINE_PARAMS)
    plot.line(x='Month', y='Mulch_Leaves', source=mulch_source,
              legend='Leaves', color=next(color_iter), **LINE_PARAMS)

    plot.xaxis.axis_label = "Month"
    plot.yaxis.axis_label = "Pounds"

    def _update_plot_yaxis(**kwargs):
        plot.yaxis.axis_label = UNIT_CONVERSION_MAP[kwargs['units']]

    ELEMENT_CALLBACKS.append(_update_plot_yaxis)
    return plot


def mulch_summary_data(sources):
    df = sources['sources']['mulch'].to_df()
    message = f'<h3>Tons of Leaves: {len(df)}</h3>'
    mulch_summary = Div(text=message, width=200, height=50)

    def _update_mulch_summary(**kwargs):
        df = kwargs['sources']['sources']['mulch'].to_df()
        mulch_summary.text = f'<h3>Tons of Leaves: {len(df)}</h3>'

    ELEMENT_CALLBACKS.append(_update_mulch_summary)
    return mulch_summary


def main():
    catalog_filename = 'catalog.yml'
    sources = fetch_bokeh_sources(catalog_filename)

    output_file('visualization.html')

    mulch_panel = Panel(child=layout([
        mulch_line_plot(sources), mulch_summary_data(sources)
    ]), title="Mulch")

    commodity_recycling_panel = Panel(child=layout([
        mulch_line_plot(sources),
        mulch_line_plot(sources)
    ]), title="Commodity Recycling")

    return layout([
        source_filters(sources),
        Tabs(tabs=[
            mulch_panel,
            commodity_recycling_panel
        ])
    ])


curdoc().add_root(main())