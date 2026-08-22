"""Painel de métricas e aprendizado do estúdio de vídeo."""

from __future__ import annotations

from typing import Any

import streamlit as st

from .agents import AgentOrchestrator
from .memory_store import record_learning
from .project_store import list_projects, load_project

import metrics_store


PLATFORM_LABELS = {"tiktok": "TikTok", "youtube": "YouTube", "instagram": "Instagram"}


def _project_id() -> str | None:
    value = st.session_state.get("nexus_video_project_id")
    return str(value) if value else None


def _format_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted = []
    for row in rows:
        formatted.append(
            {
                "Projeto": row.get("project_id"),
                "Canal": PLATFORM_LABELS.get(row.get("platform"), row.get("platform")),
                "Status": row.get("status"),
                "Views": int(row.get("views") or 0),
                "Impressões": int(row.get("impressions") or 0),
                "Curtidas": int(row.get("likes") or 0),
                "Comentários": int(row.get("comments") or 0),
                "Compartilhamentos": int(row.get("shares") or 0),
                "Conclusão": f"{float(row.get('completion_rate') or 0):.1%}",
                "Engajamento": f"{float(row.get('engagement_rate') or 0):.1%}",
                "CTR": f"{float(row.get('ctr') or 0):.1%}",
                "Seguidores": int(row.get("follower_delta") or 0),
            }
        )
    return formatted


def _register_publication(project_id: str) -> None:
    projects = [item for item in list_projects() if item.project_id == project_id]
    if projects:
        metrics_store.register_video_project(projects[0].to_dict())
    platform = st.session_state.get(f"metrics_platform_{project_id}", "tiktok")
    external_id = st.session_state.get(f"metrics_external_id_{project_id}") or None
    external_url = st.session_state.get(f"metrics_external_url_{project_id}") or None
    status = st.session_state.get(f"metrics_status_{project_id}", "published")
    metrics_store.record_video_publication(project_id, platform, external_post_id=external_id, external_url=external_url, status=status)


def _recommend(project_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    project = load_project(project_id)
    summary = {
        "platform_rows": rows,
        "views": sum(int(row.get("views") or 0) for row in rows),
        "impressions": sum(int(row.get("impressions") or 0) for row in rows),
        "clicks": sum(int(row.get("clicks") or 0) for row in rows),
        "duration_seconds": project.total_duration_seconds,
        "product_name": project.product_name,
    }
    result = AgentOrchestrator().run("analista", {"product_name": project.product_name, "metrics": summary, "duration_seconds": project.total_duration_seconds})
    output = result.output
    for insight in output.get("recommendations", []):
        record_learning(source=f"metrics:{project_id}", insight=str(insight), confidence=output.get("confidence", "low"), evidence=summary, tags=["metricas", "video"])
    return output


def exibir_painel_metricas() -> None:
    st.header("📈 Métricas e aprendizado")
    st.caption("Registre dados reais do TikTok, YouTube ou Instagram e gere hipóteses de teste. O painel não fabrica views nem trata projeções como resultado.")
    project_id = _project_id()
    if not project_id:
        st.info("Abra um projeto na aba Máquina de Vídeos para registrar métricas.")
        return
    try:
        project = load_project(project_id)
    except FileNotFoundError:
        st.warning("O projeto selecionado não foi encontrado.")
        return

    st.markdown(f"**Projeto:** {project.title} · versão {project.version} · duração {project.total_duration_seconds:.1f}s")
    with st.expander("Registrar ou atualizar publicação", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.selectbox("Plataforma", list(PLATFORM_LABELS), format_func=lambda value: PLATFORM_LABELS[value], key=f"metrics_platform_{project_id}")
        with col_b:
            st.text_input("ID do post", key=f"metrics_external_id_{project_id}")
        with col_c:
            st.text_input("URL pública", key=f"metrics_external_url_{project_id}")
        st.selectbox("Status", ["published", "draft", "failed", "removed"], index=0, key=f"metrics_status_{project_id}")
        if st.button("Salvar publicação", key=f"metrics_save_publication_{project_id}"):
            try:
                _register_publication(project_id)
                st.success("Publicação registrada; agora informe as métricas reais.")
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível registrar a publicação: {exc}")

    publications = metrics_store.list_video_publications(project_id)
    if not publications:
        st.info("Nenhuma publicação registrada para este projeto.")
        return
    publication_labels = [f"#{row['id']} · {PLATFORM_LABELS.get(row['platform'], row['platform'])} · {row['status']}" for row in publications]
    selected_index = st.selectbox("Publicação para medir", range(len(publication_labels)), format_func=lambda index: publication_labels[index], key=f"metrics_publication_selector_{project_id}")
    publication_id = int(publications[selected_index]["id"])

    with st.expander("Registrar leitura de métricas", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        views = c1.number_input("Views", min_value=0, step=1, key=f"metric_views_{project_id}")
        impressions = c2.number_input("Impressões", min_value=0, step=1, key=f"metric_impressions_{project_id}")
        avg_watch = c3.number_input("Tempo médio (s)", min_value=0.0, step=0.5, key=f"metric_watch_{project_id}")
        completed = c4.number_input("Views completas", min_value=0, step=1, key=f"metric_completed_{project_id}")
        c5, c6, c7, c8, c9 = st.columns(5)
        likes = c5.number_input("Curtidas", min_value=0, step=1, key=f"metric_likes_{project_id}")
        comments = c6.number_input("Comentários", min_value=0, step=1, key=f"metric_comments_{project_id}")
        shares = c7.number_input("Compartilhamentos", min_value=0, step=1, key=f"metric_shares_{project_id}")
        clicks = c8.number_input("Cliques", min_value=0, step=1, key=f"metric_clicks_{project_id}")
        followers = c9.number_input("Seguidores +/-", step=1, key=f"metric_followers_{project_id}")
        if st.button("Guardar métricas", type="primary", key=f"metrics_save_values_{project_id}"):
            if completed > views and views > 0:
                st.error("Views completas não podem exceder views.")
            elif clicks > impressions and impressions > 0:
                st.error("Cliques não podem exceder impressões.")
            else:
                metrics_store.record_video_metrics(publication_id, views=int(views), impressions=int(impressions), avg_watch_time_seconds=float(avg_watch), completed_views=int(completed), likes=int(likes), comments=int(comments), shares=int(shares), clicks=int(clicks), follower_delta=int(followers))
                st.success("Métricas reais guardadas.")
                st.rerun()

    rows = metrics_store.video_performance_rows(project_id)
    if rows:
        st.markdown("#### Desempenho consolidado por canal")
        st.dataframe(_format_rows(rows), use_container_width=True, hide_index=True)
        total_views = sum(int(row.get("views") or 0) for row in rows)
        total_likes = sum(int(row.get("likes") or 0) for row in rows)
        total_comments = sum(int(row.get("comments") or 0) for row in rows)
        total_shares = sum(int(row.get("shares") or 0) for row in rows)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Views", total_views)
        k2.metric("Curtidas", total_likes)
        k3.metric("Comentários", total_comments)
        k4.metric("Compartilhamentos", total_shares)
        if st.button("Analisar e registrar aprendizado", key=f"metrics_analyze_{project_id}"):
            try:
                output = _recommend(project_id, rows)
                st.success("Hipóteses registradas na memória do projeto.")
                for recommendation in output.get("recommendations", []):
                    st.info(recommendation)
            except Exception as exc:
                st.error(f"A análise não pôde ser concluída: {exc}")


__all__ = ["exibir_painel_metricas"]
