from dash import html, dcc
from dash.dependencies import Input, Output
from home import create_page_home
from charts import create_charts
from anomaly import create_anomaly
from app import app
import dash

application = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])

def display_page(pathname):
    if pathname == '/analytics':
        return create_charts()
    if pathname == '/anomaly':
        return create_anomaly()
    else:
        return create_page_home()


if __name__ == '__main__':
    app.run_server(debug=False)
