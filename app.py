import dash
from dash import html, dcc
from dash import Input, Output, State
import base64
import re
import sys
import pandas as pd

sys.path.append('./pages')
sys.path.append('./utils')

from menage import ManageRecommendation

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

manage = ManageRecommendation()
ids = ''

app.layout = html.Div([
    html.Button("Wyloguj", id="logout-button"),
    html.P('Jeśli nic się nie dzieje na stronie - zobacz tytuł okna - jeśli jest `updating` - poczekaj',style={'fontSize':'8px','textAlign':'center'}),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

encoded_logo = base64.b64encode(open('assets/spotify-logo.png', 'rb').read()).decode()

login_page = html.Div([
    html.H3('Zaloguj się do Spotify'),
    html.P('i podaj link do playlisty którą chcesz sprawdzić, pod kątem rekomendacji'),
    dcc.Link(
        html.Button([
            html.Div([
                html.Img(src=f'data:image/png;base64,{encoded_logo}', height='30px', style={'marginRight': '10px'}),
                html.Div('Zaloguj z Spotify', style={'fontWeight': 'bold'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], style={'borderRadius': '12px','padding': '10px 20px','cursor': 'pointer','textAlign': 'left','lineHeight': '1.5','height': 'auto'}),
        href='/playlist'
    ) 
], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'height': '100vh'} )

playlist_page = html.Div([
            html.H3('Wpisz swój adres URL playlisty:'),
            dcc.Input(id='playlist-input-1', type='text', value='', style={'width':'70%'}),
            html.Br(),
            html.Button('Pokaż rekomendacje', id='playlist-button-1', n_clicks=0),
            html.Br(),
            dcc.Location(id='playlist-url', refresh=False),
            html.Div(id='playlist-output-1'),
        ], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'height': '100vh'})

def get_playlist_id(url):
    if url.startswith("https://open.spotify.com/playlist/") or url.startswith("open.spotify.com/playlist/"):
        match = re.search(r"/playlist/([a-zA-Z0-9]+)", url)
        if match:
            return match.group(1)
        else:
            return False
    else:
        return False

@app.callback(
    Output('playlist-output-1', 'children'),
    [Input('playlist-button-1', 'n_clicks')],
    [State('playlist-input-1', 'value')]
)
def redirect_to_next_page(n_clicks, value):
    if n_clicks > 0:
        if value:
            global ids
            ids = get_playlist_id(value)
            if ids and ids != '':
                manage.create_recommendation_engine()
                manage.train_recommendation_engine()
                return dcc.Location(pathname=f'/recomendation', id='redirect-url')
            else:
                return html.P("Wpisz poprawny URL playlisty przed przejściem dalej.")
        else:
            return html.P("Wpisz adres URL playlisty przed przejściem dalej.")
 
def create_recomendation_page():
        if not ids:
            return html.Div([html.A('Wróć do poprzedniej strony', href='/playlist')],
                            style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center',
                                   'alignItems': 'center', 'height': '100vh'})
        preds, names, name = manage.make_predictions(ids)
        df = pd.DataFrame(data={'names': names,'preds':preds})
        df_1 = df[df['preds'] == 1]
        recom = len(df_1) / len(df)
        songs = df_1['names']

        recom_page = html.Div([
            html.P(name, style={'fontWeight':300, 'fontSize': '24px'}),
            html.Br(),
            html.H3('Rekomendacja dotycząca podanej playlisty'),
            html.H5(f'Playlista jest rekomendowana w {round(recom * 100,2)}%', style={'fontWeight':'bold'}),
            html.P(f'Zarekomendowano ci {len(df_1)} / {len(df)} piosenek'),
            html.A('Wróć do poprzedniej strony', href='/playlist'),
            html.Br(),
            html.Hr(),
            html.H3('Te piosenki mogą ci się spodobać:'),
            html.Ul([html.Li(song) for song in songs]),
        ], style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center',
                                                        'alignItems': 'center', 'height': 'auto'})
        
        return recom_page

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    """
    Obsługuje wyświetlanie strony w zależności od ścieżki URL.
    """
    if pathname == '/':
        return login_page
    elif pathname == '/playlist':
        if not manage.spotify_loader:
            manage.authorize_spotify(['user-library-read','user-top-read'])
            manage.load_data()
            manage.load_data_for_recomendation()
        return playlist_page
    elif pathname == '/recomendation':
        return create_recomendation_page()

@app.callback(
    Output('url', 'pathname'),
    [Input('logout-button', 'n_clicks')]
)
def handle_logout(n_clicks):
    if n_clicks:
        manage.logout()
        return '/'

if __name__ == '__main__':
    app.run_server(debug=False)
