"""
Data Visualization Utility Module
Provides standardized, cricket-themed interactive Plotly visual generators.
"""

import plotly.express as px
import plotly.graph_objects as go

# Visual Theme Palette
COLOR_BG = '#0B1220'
COLOR_CARD = '#111C2E'
COLOR_TEXT = '#F8FAFC'
COLOR_MUTED = '#94A3B8'
COLOR_GRID = '#1E293B'
COLOR_PRIMARY = '#16A34A'   # Grass Green
COLOR_SECONDARY = '#38BDF8' # Sky Blue
COLOR_ACCENT = '#F59E0B'    # Cricket Gold
COLOR_DANGER = '#EF4444'    # Out Red
COLOR_PURPLE = '#A855F7'    # Royal Purple

CHART_PALETTE = ['#16A34A', '#38BDF8', '#F59E0B', '#A855F7', '#EC4899', '#14B8A6', '#F97316', '#6366F1']

def apply_custom_theme(fig, title="", height=450):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLOR_CARD,
        plot_bgcolor=COLOR_CARD,
        font=dict(family="Inter, Segoe UI, sans-serif", color=COLOR_TEXT, size=12),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=16, color=COLOR_TEXT),
            x=0.02,
            y=0.96
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor=COLOR_BG,
            font_size=12,
            font_family="Inter, sans-serif",
            font_color=COLOR_TEXT
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLOR_MUTED)
        ),
        xaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            tickfont=dict(color=COLOR_MUTED),
            titlefont=dict(color=COLOR_TEXT)
        ),
        yaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            tickfont=dict(color=COLOR_MUTED),
            titlefont=dict(color=COLOR_TEXT)
        )
    )
    return fig

def create_horizontal_bar(df, x_col, y_col, title, color_col=None, text_col=None, height=450):
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        orientation='h',
        color=color_col or x_col,
        color_continuous_scale=[[0, '#0284C7'], [1, '#16A34A']],
        text=text_col or x_col
    )
    fig.update_traces(
        texttemplate='%{text:,.2f}' if df[x_col].dtype == 'float64' else '%{text:,.0f}',
        textposition='outside',
        marker=dict(line=dict(width=0))
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    return apply_custom_theme(fig, title, height)

def create_vertical_bar(df, x_col, y_col, title, color_col=None, text_col=None, height=450):
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        color_discrete_sequence=CHART_PALETTE,
        text=text_col or y_col
    )
    fig.update_traces(
        textposition='outside',
        texttemplate='%{text:,.2f}' if df[y_col].dtype == 'float64' else '%{text:,.0f}'
    )
    return apply_custom_theme(fig, title, height)

def create_line_chart(df, x_col, y_col, title, color_col=None, markers=True, height=450):
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        markers=markers,
        color_discrete_sequence=CHART_PALETTE
    )
    fig.update_traces(line=dict(width=3))
    return apply_custom_theme(fig, title, height)

def create_donut_chart(df, names_col, values_col, title, height=420):
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.55,
        color_discrete_sequence=CHART_PALETTE
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color=COLOR_BG, width=2)))
    return apply_custom_theme(fig, title, height)

def create_scatter_plot(df, x_col, y_col, title, size_col=None, color_col=None, hover_name=None, height=480):
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        hover_name=hover_name,
        color_continuous_scale=[[0, '#38BDF8'], [1, '#16A34A']],
        size_max=35
    )
    return apply_custom_theme(fig, title, height)

def create_radar_chart(categories, player1_name, player1_vals, player2_name=None, player2_vals=None, title="", height=480):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=player1_vals + [player1_vals[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=player1_name,
        line=dict(color=COLOR_PRIMARY, width=2),
        fillcolor='rgba(22, 163, 74, 0.3)'
    ))

    if player2_name and player2_vals:
        fig.add_trace(go.Scatterpolar(
            r=player2_vals + [player2_vals[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=player2_name,
            line=dict(color=COLOR_SECONDARY, width=2),
            fillcolor='rgba(56, 189, 248, 0.3)'
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=COLOR_GRID, linecolor=COLOR_GRID, tickfont=dict(color=COLOR_MUTED)),
            angularaxis=dict(gridcolor=COLOR_GRID, linecolor=COLOR_GRID, tickfont=dict(color=COLOR_TEXT, size=12)),
            bgcolor=COLOR_CARD
        ),
        paper_bgcolor=COLOR_CARD,
        font=dict(color=COLOR_TEXT, family="Inter, sans-serif"),
        title=dict(text=f"<b>{title}</b>", font=dict(size=16, color=COLOR_TEXT)),
        legend=dict(font=dict(color=COLOR_TEXT)),
        height=height
    )
    return fig

def create_worm_chart(df_inns1, df_inns2, team1_name, team2_name, title="Innings Progression (Worm Chart)", height=450):
    fig = go.Figure()
    
    if df_inns1 is not None and not df_inns1.empty:
        fig.add_trace(go.Scatter(
            x=df_inns1['over_ball'],
            y=df_inns1['cumulative_runs'],
            mode='lines',
            name=f"{team1_name} (1st Inns)",
            line=dict(color=COLOR_PRIMARY, width=3)
        ))
        # Add wicket markers
        wickets1 = df_inns1[df_inns1['is_wicket'] == 1]
        if not wickets1.empty:
            fig.add_trace(go.Scatter(
                x=wickets1['over_ball'],
                y=wickets1['cumulative_runs'],
                mode='markers',
                name=f"{team1_name} Wickets",
                marker=dict(symbol='x', color=COLOR_DANGER, size=9)
            ))
            
    if df_inns2 is not None and not df_inns2.empty:
        fig.add_trace(go.Scatter(
            x=df_inns2['over_ball'],
            y=df_inns2['cumulative_runs'],
            mode='lines',
            name=f"{team2_name} (2nd Inns)",
            line=dict(color=COLOR_SECONDARY, width=3)
        ))
        wickets2 = df_inns2[df_inns2['is_wicket'] == 1]
        if not wickets2.empty:
            fig.add_trace(go.Scatter(
                x=wickets2['over_ball'],
                y=wickets2['cumulative_runs'],
                mode='markers',
                name=f"{team2_name} Wickets",
                marker=dict(symbol='x', color=COLOR_ACCENT, size=9)
            ))
            
    fig.update_layout(
        xaxis_title="Over",
        yaxis_title="Total Runs",
        hovermode="x unified"
    )
    return apply_custom_theme(fig, title, height)
