"""Interface do estúdio de vídeo integrado ao Nexus Master."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

import campaign_state

from .agents import AGENT_SPECS, AgentOrchestrator
from .memory_store import recent_context, record_agent_run
from .project_store import add_scene, create_project, list_projects, load_project, remove_scene, save_project, update_scene
from .render_engine import render_project
from .validation import validation_summary


SESSION_PROJECT = "nexus_video_project_id"


def _current_project():
    project_id = st.session_state.get(SESSION_PROJECT)
    if not project_id:
        return None
    try:
        return load_project(project_id)
    except (FileNotFoundError, ValueError, TypeError, KeyError):
        st.session_state.pop(SESSION_PROJECT, None)
        return None


def _campaign_context(project) -> dict[str, Any]:
    campaign = campaign_state.get_campaign()
    return {
        "project_id": project.project_id,
        "product_name": project.product_name or campaign.get("product_name"),
        "niche": project.niche or campaign.get("niche"),
        "platform": project.platform,
        "duration_seconds": project.target_duration_seconds,
        "tone": project.tone,
        "goal": project.goal,
        "source_image_url": campaign.get("source_image_url") or campaign.get("image_url"),
        "metrics": st.session_state.get("nexus_video_metrics", {}),
    }


def _apply_script(project, output: dict[str, Any]) -> None:
    scenes = output.get("scenes") or []
    project.scenes = []
    for item in scenes:
        add_scene(
            project,
            label=item.get("label", "Cena"),
            text=item.get("text", ""),
            duration_seconds=item.get("duration_seconds", 3),
            visual_prompt=item.get("visual_prompt", ""),
            caption=item.get("caption", item.get("text", "")),
        )
    project.disclosure = str(output.get("disclosure") or project.disclosure)


def _run_agents(project) -> dict[str, Any]:
    orchestrator = AgentOrchestrator()
    context = _campaign_context(project)
    outputs: dict[str, Any] = {}
    order = ["estrategia", "roteiro", "direcao_visual", "edicao", "voz_legendas", "thumbnail", "conformidade"]
    for agent_id in order:
        result = orchestrator.run(agent_id, context)
        project.agent_runs.append(result.to_dict())
        project.agent_runs = project.agent_runs[-40:]
        record_agent_run(
            project_id=project.project_id,
            agent_id=result.agent_id,
            provider=result.provider,
            model=result.model,
            output=result.output,
            used_fallback=result.used_fallback,
            error=result.error,
        )
        outputs[agent_id] = result.output
        if agent_id == "roteiro":
            _apply_script(project, result.output)
        elif agent_id == "edicao":
            canvas = result.output.get("canvas", {})
            project.width = int(canvas.get("width", project.width))
            project.height = int(canvas.get("height", project.height))
            project.fps = int(canvas.get("fps", project.fps))
            project.duration_limit_seconds = min(int(canvas.get("max_duration_seconds", project.duration_limit_seconds)), 900)
        elif agent_id == "conformidade":
            project.compliance = result.output
    project.memory_tags = ["agentes-executados", project.platform.lower().replace(" ", "-")]
    project.status = "review"
    save_project(project)
    campaign_state.set_campaign(
        video_project_id=project.project_id,
        script={"title": outputs.get("roteiro", {}).get("title"), "scenes": [scene.to_dict() for scene in project.scenes]},
        prompt=outputs.get("direcao_visual", {}).get("image_prompts", [""])[0],
        video_project_manifest=project.to_dict(),
    )
    return outputs


def _render_agent_cards(project) -> None:
    st.markdown("#### Equipe de IA")
    latest: dict[str, dict[str, Any]] = {}
    for item in project.agent_runs:
        latest[item.get("agent_id", "")] = item
    columns = st.columns(4)
    for index, (agent_id, spec) in enumerate(AGENT_SPECS.items()):
        item = latest.get(agent_id)
        with columns[index % 4]:
            if item:
                mode = "local" if item.get("used_fallback") else item.get("provider", "remoto")
                st.metric(spec.name, mode, help=spec.specialty)
            else:
                st.metric(spec.name, "pendente", help=spec.specialty)


def _render_scene_editor(project) -> None:
    st.markdown("#### Linha do tempo editável")
    st.caption("Edite cada cena, duração e legenda. O total é limitado a 15 minutos e nada é publicado automaticamente.")
    if not project.scenes:
        st.info("Execute a equipe de IA ou adicione uma cena manualmente.")
    for index, scene in enumerate(list(project.scenes), start=1):
        with st.expander(f"Cena {index} · {scene.label} · {scene.duration_seconds:.1f}s", expanded=index == 1):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                label = st.text_input("Rótulo", value=scene.label, key=f"scene_label_{project.project_id}_{scene.scene_id}")
                text = st.text_area("Texto principal", value=scene.text, height=100, key=f"scene_text_{project.project_id}_{scene.scene_id}")
                caption = st.text_area("Legenda", value=scene.caption, height=80, key=f"scene_caption_{project.project_id}_{scene.scene_id}")
                visual_prompt = st.text_area("Prompt visual", value=scene.visual_prompt, height=80, key=f"scene_prompt_{project.project_id}_{scene.scene_id}")
            with col_b:
                duration = st.number_input("Duração (s)", min_value=0.5, max_value=120.0, value=float(scene.duration_seconds), step=0.5, key=f"scene_duration_{project.project_id}_{scene.scene_id}")
                enabled = st.checkbox("Cena ativa", value=scene.enabled, key=f"scene_enabled_{project.project_id}_{scene.scene_id}")
                if st.button("Salvar cena", key=f"scene_save_{project.project_id}_{scene.scene_id}", use_container_width=True):
                    update_scene(project, scene.scene_id, label=label, text=text, caption=caption, visual_prompt=visual_prompt, duration_seconds=duration, enabled=enabled)
                    save_project(project)
                    st.success("Cena salva.")
                    st.rerun()
                if st.button("Remover", key=f"scene_remove_{project.project_id}_{scene.scene_id}", use_container_width=True):
                    remove_scene(project, scene.scene_id)
                    save_project(project)
                    st.rerun()
    if st.button("+ Adicionar cena", key=f"scene_add_{project.project_id}"):
        add_scene(project, label="Nova cena", text="Escreva a mensagem principal", duration_seconds=3, caption="Escreva a legenda")
        save_project(project)
        st.rerun()
    st.caption(f"Duração ativa: **{project.total_duration_seconds:.1f}s** · Limite: **{project.duration_limit_seconds}s**")


def _render_assets(project) -> None:
    st.markdown("#### Exportação")
    if project.render_path and Path(project.render_path).is_file():
        st.video(project.render_path)
        st.download_button("Baixar vídeo MP4", Path(project.render_path).read_bytes(), file_name=f"{project.project_id}.mp4", mime="video/mp4", key=f"download_video_{project.project_id}")
    if project.thumbnail_path and Path(project.thumbnail_path).is_file():
        st.image(project.thumbnail_path, caption="Thumbnail editável gerada pelo renderizador local", width=260)
        st.download_button("Baixar thumbnail", Path(project.thumbnail_path).read_bytes(), file_name=f"{project.project_id}_thumbnail.jpg", mime="image/jpeg", key=f"download_thumb_{project.project_id}")
    if project.subtitle_path and Path(project.subtitle_path).is_file():
        st.download_button("Baixar legendas VTT", Path(project.subtitle_path).read_bytes(), file_name=f"{project.project_id}.vtt", mime="text/vtt", key=f"download_vtt_{project.project_id}")


def _render_memory(project) -> None:
    context = recent_context(project_id=project.project_id, limit=5)
    with st.expander("Memória do projeto", expanded=False):
        st.write("A memória registra decisões e resultados observáveis para orientar os próximos ciclos.")
        if context["recent_learnings"]:
            for item in reversed(context["recent_learnings"]):
                st.markdown(f"- **{item.get('confidence', 'low')}** · {item.get('insight', '')}")
        else:
            st.caption("Nenhum aprendizado de métricas foi registrado ainda.")
        if context["recent_runs"]:
            st.caption(f"Execuções de agentes registradas: {len(context['recent_runs'])}")


def exibir_maquina_videos() -> None:
    st.header("🎬 Máquina de Vídeos Nexus")
    st.caption("Estúdio vertical com agentes especializados, edição por cenas, memória e exportação manual. O sistema não promete viralização e não publica sem revisão.")

    campaign = campaign_state.get_campaign()
    projects = list_projects()
    top_a, top_b, top_c = st.columns([2, 2, 1])
    with top_a:
        product = st.text_input("Produto, tema ou assunto", value=campaign.get("product_name", ""), key="video_new_product")
    with top_b:
        niche = st.text_input("Nicho e público", value=campaign.get("niche", ""), key="video_new_niche")
    with top_c:
        platform = st.selectbox("Canal", ["TikTok", "YouTube Shorts", "Instagram Reels"], key="video_new_platform")
    if st.button("Criar projeto", type="primary", key="video_create_project"):
        if not product.strip():
            st.warning("Informe um produto, tema ou assunto.")
        else:
            project = create_project(product.strip(), niche=niche.strip(), platform=platform, target_duration_seconds=24)
            save_project(project)
            st.session_state[SESSION_PROJECT] = project.project_id
            campaign_state.set_campaign(product_name=project.product_name, niche=project.niche, video_project_id=project.project_id)
            st.rerun()

    if projects:
        labels = [f"{item.title} · {item.status} · v{item.version}" for item in projects]
        selected_index = st.selectbox("Projetos salvos", range(len(labels)), format_func=lambda index: labels[index], key="video_project_selector")
        selected_id = projects[selected_index].project_id
        if st.session_state.get(SESSION_PROJECT) != selected_id:
            st.session_state[SESSION_PROJECT] = selected_id
            st.rerun()

    project = _current_project()
    if project is None:
        st.info("Crie ou selecione um projeto para abrir o estúdio.")
        return

    st.divider()
    meta_a, meta_b, meta_c, meta_d = st.columns([2, 1, 1, 1])
    with meta_a:
        title = st.text_input("Nome do projeto", value=project.title, key=f"video_title_{project.project_id}")
    with meta_b:
        project.target_duration_seconds = int(st.number_input("Duração alvo (s)", min_value=6, max_value=int(project.duration_limit_seconds), value=min(int(project.target_duration_seconds), int(project.duration_limit_seconds)), step=1, key=f"video_duration_{project.project_id}"))
    with meta_c:
        project.tone = st.text_input("Tom", value=project.tone, key=f"video_tone_{project.project_id}")
    with meta_d:
        st.metric("Versão", project.version)
    project.title = title
    project.platform = platform if platform else project.platform
    st.caption(f"Preset: 9:16 · Limite aplicado a este canal: {project.duration_limit_seconds}s · revisão humana obrigatória antes de publicar")
    if st.button("Salvar configurações", key=f"video_save_meta_{project.project_id}"):
        save_project(project)
        st.success("Configurações salvas.")

    source = st.file_uploader("Imagem ou vídeo-fonte opcional", type=["jpg", "jpeg", "png", "webp"], key=f"video_source_{project.project_id}")
    if source is not None:
        source_dir = Path(".nexus_media") / "video_projects" / project.project_id
        source_dir.mkdir(parents=True, exist_ok=True)
        source_path = source_dir / f"source_{source.name}"
        source_path.write_bytes(source.getbuffer())
        project.source_image_path = str(source_path)
        save_project(project)
        st.success("Fonte visual guardada no projeto.")

    if st.button("Executar equipe de IA", type="primary", key=f"video_run_agents_{project.project_id}", use_container_width=True):
        with st.spinner("Estrategista, roteirista, diretor visual, editor, voz, thumbnail e conformidade trabalhando..."):
            outputs = _run_agents(project)
        st.success(f"Projeto atualizado com {len(outputs)} agentes. Revise as cenas antes de exportar.")
        st.rerun()

    _render_agent_cards(project)
    _render_scene_editor(project)

    render_a, render_b = st.columns([1, 2])
    with render_a:
        if st.button("Renderizar MP4", type="primary", key=f"video_render_{project.project_id}", use_container_width=True):
            gate = validation_summary(project)
            for warning in gate["warnings"]:
                st.warning(warning["message"])
            if not gate["ok"]:
                for issue in gate["blocking"]:
                    st.error(issue["message"])
            else:
                try:
                    with st.spinner("Renderizando cenas, legendas e thumbnail..."):
                        result = render_project(project)
                    st.success(f"Render concluído: {result['total_duration_seconds']:.1f}s.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Renderização não concluída: {exc}")
    with render_b:
        if project.compliance:
            status = project.compliance.get("status", "review")
            st.info(f"Revisão de conformidade: **{status}**. Verifique direitos, alegações, publicidade e áreas seguras antes de publicar.")
        else:
            st.caption("Execute a equipe de IA para gerar a checklist de conformidade.")

    _render_assets(project)
    _render_memory(project)


__all__ = ["exibir_maquina_videos"]
