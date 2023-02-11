import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import plotly.graph_objs as go
import pandas as pd
import datetime   #日期時間,用於：datetime.datetime.now()

#1. 資料準備區：讀取資料並準備好經濟指標

app = dash.Dash()               #宣告Dash

df = pd.read_csv("WBIndexCH.csv") #拉進資料
available_indicators = df['Indicator'].unique() 
# unique() 方法，處理 DataFrame 時使用，並返回一列的所有唯一元素。
#取出經濟指標名稱，做為搜尋工具。

#2. 標題區：建立自變項
app.layout = html.Div([
    html.H2(children='1960-2030年 經濟大數據動態分析'),
    html.H4(children='1.數十個經濟數據計算依據是依世銀資料建立時間，因指標起始時間及國家成立時間不同，故每個經濟指標起始時間不同。(2021-2030為 預測值)'),
    html.H5(children='2.政治實體是依照世銀定義之名稱，如Euro Area為歐元區；1990年以前世銀尚未建立政體實體名稱，故1990年前本分析資料是以國家為計算基礎。'),
    html.H6('Compute [AI Algorithm] Time: ' + str(datetime.datetime.now())+', Number of Data Updated: '+str(len(df))),
    html.Hr(), #調整畫面：畫分隔線

    #左半邊：
    html.Div([
        #建立下拉式選單(Dropdown)，選項來自資料庫中的經濟指標，共27項。
        #而以生育率做為初始值。
        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='GDP growth(annual %)GDP年增長率',
                #Multi=True, #本例為經濟指標的分析，故不使用這個設定
            ),
            
            #建立圓圖選單(RadioItem)-根據資料特性及大數據資料量，採Linear－Log對數迴歸分析
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',                #初始值
                labelStyle={
                    'display': 'inline-block', #選項水平排列
                    'margin-right': '7px',     #按鈕大小
                    'font-size': '20px',       #字大小
                    'font-color':'purple',
                    'font-weight': 300,      
                },
                style={
                    'display': 'inline-block',
                    'margin-left': '7px'
                }
            )
        ],
        #左半邊的畫面調整
        style={'width': '48%','display': 'inline-block'}), 

        #右半邊：
        html.Div([  
            #建立下拉式選單(Dropdown)，選項來自資料庫中的經濟指標，共27項。
            #而以生育率做為初始值。
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators], #引入經濟指標
                value='Life expectancy at birth, total (years)平均壽命',           #下拉式選單的初始值
                #Multi=True,
            ),
            
            #建立圓圖選單(RadioItem)-根據資料特性及大數據資料量，採Linear－Log對數迴歸分析
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',                #初始值
                labelStyle={
                    'display': 'inline-block', #選項水平排列
                    'margin-right': '7px',     #按鈕大小
                    'font-size': '20px',       #字大小
                    'font-weight': 300
                },
                style={
                    'display': 'inline-block',
                    'margin-left': '7px'
                }
            )
        ], 
        #右半邊的畫面調整
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'}) 
    ], 
    #全畫面的調整
    style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(255,204,203)', #上方橫框底色
        'padding': '5px 5px' #調整畫面邊緣空間
    }),

    #圖形產生器(plotly 圖形):
    #1. 右上圖之初始值為United States
    #2. 調整畫面為佔全畫面48%
    #3. 逐點畫出
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'United States'}]}           #初始值為United States
        )
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 20'}   #畫面調整
    ), 

    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '48%'}  #畫面調整
    ), 

    html.Div(
        #滑動軸：可點選年份，並由互動區程式立即更新所有圖形
        dcc.Slider(
            id='crossfilter-year-slider',
            min=df['Year'].min(),   #滑動軸最小值
            max=df['Year'].max(),   #滑動軸最大值
            value=df['Year'].max(), #以該指標的最大值為初始值
            step=None,
            marks={str(year): str(year) for year in df['Year'].unique()} #滑動軸的標示資料(年份)
    ), style={'width': '98%', 'padding': '0px 20px 20px 20px'}  #畫面調整
    ), 
    html.Hr(), #調整畫面：畫分隔線
])


# 3.互動控制（針對左半邊）：下拉式選單及按鈕選項產生改變時，立即重新整理圖形(封裝了React.js)
@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
        dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
        dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
        dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
        dash.dependencies.Input('crossfilter-year-slider', 'value')])

#自訂函數－互動控制(針對左半邊)：根據使用者對指標的更改，重新畫出左邊散點圖
def update_graph(xaxis_column_name, yaxis_column_name,
                    xaxis_type, yaxis_type,
                    year_value):
    dff = df[df['Year'] == year_value]
    #以下是回傳最後結果給圖形產生器
    #1. 散點的值
    #2. 散點大小
    #3. Linear/Log的最新選擇並重新運算
    #4. Plotly.graph_objs  [ 第一步驟] .Scatter() 創建圖表對象
    #                      [ 第二步驟] .Layout()  創建布局對象
    #                      [ 第三步驟] .Figure()  創建接收前兩步得到的圖表對象和布局對象，然後show出来
    return {
        
        
        # .Scatter()的係數參考https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scatter.html#plotly.graph_objects.Scatter
        'data': [go.Scatter(
            x=dff[dff['Indicator'] == xaxis_column_name]['Value'],
            y=dff[dff['Indicator'] == yaxis_column_name]['Value'],
            text=dff[dff['Indicator'] == yaxis_column_name]['PoliticalEntity'],
            customdata=dff[dff['Indicator'] == yaxis_column_name]['PoliticalEntity'],
            mode='markers',
            # markers，就是散點圖
            # lines，就是線性圖
            #設定圓形小圖的規格，大小：30,透明度：50%即半透明，圓圖外框為0.5線寛，框色為紅色
            marker={
                'size': 30,
                'opacity': 0.5,
                'color': 'rgb(255,204,203)',
                'line': {'width': 1, 'color': 'red'}
            }
        )],
        
        
        # .Layout()的係數參考 https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html#plotly.graph_objects.Layout
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }

#自訂函數－互動控制(針對左半邊)：創建圖形對象的函數
def create_time_series(dff, axis_type, title):
    return {
        'data': [go.Scatter(
            x=dff['Year'],
            y=dff['Value'],
            mode='lines+markers',
            #設定圓形小圖的規格，大小：30,透明度：50%即半透明，圓圖外框為0.5線寛，框色為藍色
            marker={
                'size': 15,
                'opacity': 1,
                'color': 'rgb(122, 213, 230)',
                'line': {'width': 1, 'color': 'red'}
            }
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 50, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title+'  趨勢分析'
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': True}
        }
    }

# 互動控制（針對右半邊上半）：當滑鼠移動到圖中自動產生標示數據(封裝了React.js)
@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
        dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
        dash.dependencies.Input('crossfilter-xaxis-type', 'value')])

#當滑鼠移動到任意點時，顯示項目，類型或圖形會更改
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['PoliticalEntity'] == country_name]
    dff = dff[dff['Indicator'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)

#互動控制（針對右半邊下半）：當滑鼠移動到圖中自動產生標示數據(封裝了React.js)
@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
        dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
        dash.dependencies.Input('crossfilter-yaxis-type', 'value')])

#當滑鼠移動到任意點時，顯示項目，類型或圖形會更改
def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    dff = df[df['PoliticalEntity'] == hoverData['points'][0]['customdata']]
    dff = dff[dff['Indicator'] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)

def generate_talbe(dataframe, max_rows=4):
    return html.Table(
            # Header
            [html.Tr([html.Th(col) for col in dataframe.columns])] +
            # Body
            [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))]
            )

if __name__ == '__main__':
    app.run_server(port=8000)