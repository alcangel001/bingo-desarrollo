"""
Asistente de IA para administración usando Google Gemini
Analiza métricas, genera recomendaciones y responde preguntas
"""
import os
import logging
import json
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai no está instalado. La IA no funcionará.")


class BingoAIAssistant:
    """Asistente de IA para análisis y recomendaciones del sistema de bingo"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY no configurada. La IA funcionará en modo limitado.")
            self.client = None
        elif GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                
                # Primero, listar modelos disponibles desde la API
                try:
                    available_models = genai.list_models()
                    model_names = []
                    for model in available_models:
                        if 'generateContent' in model.supported_generation_methods:
                            model_name = model.name
                            # Limpiar el nombre del modelo (remover prefijo si existe)
                            if '/' in model_name:
                                model_name = model_name.split('/')[-1]
                            model_names.append(model_name)
                            # También guardar el nombre completo
                            model_names.append(model.name)
                    
                    logger.info(f"📋 Modelos disponibles en la API: {model_names}")
                    
                    if not model_names:
                        logger.error("❌ No se encontraron modelos disponibles con generateContent")
                        self.client = None
                        return
                    
                    # Intentar usar el primer modelo disponible
                    for model_name in model_names:
                        try:
                            self.model = genai.GenerativeModel(model_name)
                            logger.info(f"✅ Modelo configurado: {model_name}")
                            self.client = self.model
                            return
                        except Exception as e:
                            logger.debug(f"Modelo {model_name} no funcionó: {str(e)}")
                            continue
                    
                    logger.error("❌ Ningún modelo disponible funcionó")
                    self.client = None
                    
                except Exception as e:
                    logger.error(f"Error listando modelos: {str(e)}")
                    # Fallback: intentar modelos conocidos
                    model_candidates = [
                        'gemini-pro',
                        'models/gemini-pro',
                    ]
                    
                    for model_name in model_candidates:
                        try:
                            self.model = genai.GenerativeModel(model_name)
                            logger.info(f"✅ Modelo configurado (fallback): {model_name}")
                            self.client = self.model
                            return
                        except:
                            continue
                    
                    logger.error("❌ No se pudo configurar ningún modelo")
                    self.client = None
            except Exception as e:
                logger.error(f"Error configurando Gemini: {str(e)}")
                self.client = None
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Verifica si la IA está disponible"""
        return self.client is not None and self.api_key is not None
    
    def analyze_dashboard_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza las métricas del dashboard y genera recomendaciones
        
        Args:
            metrics: Diccionario con todas las métricas del dashboard
            
        Returns:
            Dict con análisis, alertas y recomendaciones
        """
        if not self.is_available():
            return self._generate_basic_analysis(metrics)
        
        try:
            # Preparar contexto para la IA
            context = self._prepare_metrics_context(metrics)
            
            prompt = f"""Eres un asistente experto en análisis de plataformas de juegos online.
Analiza las siguientes métricas de la plataforma de bingo y genera:
1. Análisis de salud general del sistema (bueno/preocupante/crítico)
2. Alertas prioritarias (máximo 3)
3. Recomendaciones accionables (máximo 5)
4. Predicciones a corto plazo

Métricas:
{context}

Responde en formato JSON con esta estructura:
{{
    "health_status": "bueno|preocupante|crítico",
    "health_score": 0-100,
    "summary": "Resumen de 2-3 líneas",
    "alerts": [
        {{"type": "warning|error|info", "title": "...", "message": "...", "priority": 1-5}}
    ],
    "recommendations": [
        {{"title": "...", "description": "...", "impact": "alto|medio|bajo", "action": "..."}}
    ],
    "predictions": {{
        "revenue_next_week": "...",
        "user_growth": "...",
        "risks": ["..."]
    }}
}}"""
            
            # Generar respuesta
            response = self.client.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                }
            )
            
            # Obtener el texto de la respuesta
            if hasattr(response, 'text'):
                result_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                result_text = response.candidates[0].content.parts[0].text
            else:
                result_text = str(response)
            
            # Limpiar el texto si tiene markdown
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            # Validar que el texto no esté vacío antes de parsear JSON
            if not result_text or not result_text.strip():
                logger.warning("Respuesta de Gemini vacía, usando análisis básico")
                return self._generate_basic_analysis(metrics)
            
            try:
                analysis = json.loads(result_text)
            except json.JSONDecodeError as json_error:
                logger.error(f"Error parseando JSON de Gemini: {json_error}. Texto recibido: {result_text[:200]}")
                # Si falla el parseo, usar análisis básico
                return self._generate_basic_analysis(metrics)
            
            # Agregar timestamp
            analysis['generated_at'] = timezone.now().isoformat()
            analysis['source'] = 'gemini'
            
            return analysis
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error en análisis de IA: {error_str}")
            
            # Manejar error de cuota excedida
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                logger.warning("⚠️ Cuota de Gemini API excedida o no habilitada")
                return {
                    "health_status": "preocupante",
                    "health_score": 50,
                    "summary": "Análisis limitado: La cuota de Gemini API está excedida o no está habilitada. Verifica la facturación en Google Cloud.",
                    "alerts": [{
                        "type": "warning",
                        "title": "Cuota de IA Excedida",
                        "message": "La API de Gemini no tiene cuota disponible. Necesitas habilitar facturación o verificar límites.",
                        "priority": 4
                    }],
                    "recommendations": [{
                        "title": "Habilitar Cuota de Gemini",
                        "description": "Ve a Google Cloud Console y habilita la facturación o verifica los límites de cuota",
                        "impact": "alto",
                        "action": "Ver: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas"
                    }],
                    "predictions": {
                        "revenue_next_week": "No disponible",
                        "user_growth": "No disponible",
                        "risks": ["Cuota de IA no disponible"]
                    },
                    "generated_at": timezone.now().isoformat(),
                    "source": "quota_error"
                }
            
            return self._generate_basic_analysis(metrics)
    
    def answer_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Responde preguntas del administrador sobre el sistema
        
        Args:
            question: Pregunta del usuario
            context: Contexto opcional con métricas o datos
            
        Returns:
            Dict con respuesta y acciones sugeridas
        """
        if not self.is_available():
            return {
                "answer": "La IA no está disponible. Por favor configura GEMINI_API_KEY.",
                "confidence": 0,
                "source": "fallback"
            }
        
        try:
            context_str = ""
            if context:
                context_str = f"\n\nContexto del sistema:\n{json.dumps(context, indent=2, default=str)}"
            
            prompt = f"""Eres un asistente experto en administración de plataformas de bingo online.
Responde la siguiente pregunta del administrador de forma clara y concisa.
Si necesitas datos específicos, usa el contexto proporcionado.
Si no tienes suficiente información, di qué necesitarías para responder mejor.

Pregunta: {question}
{context_str}

Responde en formato JSON:
{{
    "answer": "Respuesta clara y concisa",
    "confidence": 0-100,
    "sources": ["métrica_x", "métrica_y"],
    "suggested_actions": ["acción 1", "acción 2"]
}}"""
            
            # Generar respuesta
            response = self.client.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                }
            )
            
            # Obtener el texto de la respuesta
            if hasattr(response, 'text'):
                result_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                result_text = response.candidates[0].content.parts[0].text
            else:
                result_text = str(response)
            
            # Limpiar el texto
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            answer = json.loads(result_text)
            answer['timestamp'] = timezone.now().isoformat()
            answer['source'] = 'gemini'
            
            return answer
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error respondiendo pregunta: {error_str}")
            
            # Manejar error de cuota excedida
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                return {
                    "answer": "Lo siento, la cuota de Gemini API está excedida o no está habilitada. Necesitas habilitar facturación en Google Cloud Console (aunque el tier gratuito no cobra). Ve a: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas",
                    "confidence": 0,
                    "sources": [],
                    "suggested_actions": [
                        "Habilitar facturación en Google Cloud (tier gratuito disponible)",
                        "Verificar límites de cuota en Google Cloud Console",
                        "Esperar a que se resetee la cuota (si es temporal)"
                    ],
                    "source": "quota_error"
                }
            
            return {
                "answer": f"Lo siento, hubo un error al procesar tu pregunta: {error_str}",
                "confidence": 0,
                "source": "error"
            }
    
    def generate_report(self, metrics: Dict[str, Any], report_type: str = "daily") -> str:
        """
        Genera un reporte automático basado en métricas
        
        Args:
            metrics: Métricas del sistema
            report_type: Tipo de reporte (daily, weekly, monthly)
            
        Returns:
            Reporte en texto formateado
        """
        if not self.is_available():
            return self._generate_basic_report(metrics, report_type)
        
        try:
            context = self._prepare_metrics_context(metrics)
            
            prompt = f"""Genera un reporte {report_type} profesional para la plataforma de bingo.
Incluye:
1. Resumen ejecutivo
2. Métricas clave
3. Alertas importantes
4. Recomendaciones
5. Próximos pasos

Métricas:
{context}

Formatea el reporte en Markdown, claro y profesional."""
            
            # Generar respuesta
            response = self.client.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                }
            )
            
            # Obtener el texto de la respuesta
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                return str(response)
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generando reporte: {error_str}")
            
            # Manejar error de cuota excedida
            if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
                report = f"# Reporte {report_type.capitalize()} - {timezone.now().strftime('%Y-%m-%d')}\n\n"
                report += "## ⚠️ Cuota de IA Excedida\n\n"
                report += "La API de Gemini no tiene cuota disponible.\n\n"
                report += "### Solución:\n"
                report += "1. Ve a [Google Cloud Console](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)\n"
                report += "2. Habilita facturación (el tier gratuito no cobra)\n"
                report += "3. Verifica los límites de cuota\n\n"
                report += "### Reporte Básico (sin IA):\n\n"
                report += self._generate_basic_report(metrics, report_type)
                return report
            
            return self._generate_basic_report(metrics, report_type)
    
    def _prepare_metrics_context(self, metrics: Dict[str, Any]) -> str:
        """Prepara las métricas en formato legible para la IA"""
        context_parts = []
        
        # Métricas financieras
        if 'platform_revenue' in metrics:
            context_parts.append(f"Ingresos de plataforma: ${metrics.get('platform_revenue', 0):.2f}")
        if 'system_balance' in metrics:
            context_parts.append(f"Balance del sistema: ${metrics.get('system_balance', 0):.2f}")
        if 'total_escrow' in metrics:
            context_parts.append(f"Fondos en escrow: ${metrics.get('total_escrow', 0):.2f}")
        
        # Métricas de usuarios
        if 'registered_users' in metrics:
            context_parts.append(f"Usuarios registrados: {metrics.get('registered_users', 0)}")
        if 'active_users' in metrics:
            context_parts.append(f"Usuarios activos (7d): {metrics.get('active_users', 0)}")
        if 'new_users_week' in metrics:
            context_parts.append(f"Nuevos usuarios (7d): {metrics.get('new_users_week', 0)}")
        
        # Métricas de actividad
        if 'active_games' in metrics:
            context_parts.append(f"Juegos activos: {metrics.get('active_games', 0)}")
        if 'active_raffles' in metrics:
            context_parts.append(f"Rifas activas: {metrics.get('active_raffles', 0)}")
        if 'problematic_games' in metrics:
            context_parts.append(f"Juegos con problemas: {metrics.get('problematic_games', 0)}")
        
        # Alertas
        if 'pending_withdrawals_count' in metrics:
            context_parts.append(f"Retiros pendientes: {metrics.get('pending_withdrawals_count', 0)}")
        if 'suspicious_transactions' in metrics:
            context_parts.append(f"Transacciones sospechosas: {metrics.get('suspicious_transactions', 0)}")
        
        return "\n".join(context_parts)
    
    def _generate_basic_analysis(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Genera análisis básico sin IA"""
        alerts = []
        recommendations = []
        
        # Análisis básico de salud
        health_score = 80
        if metrics.get('system_balance', 0) < 0:
            health_score -= 20
            alerts.append({
                "type": "error",
                "title": "Balance negativo",
                "message": "El sistema tiene balance negativo",
                "priority": 5
            })
        
        if metrics.get('pending_withdrawals_count', 0) > 10:
            health_score -= 10
            alerts.append({
                "type": "warning",
                "title": "Muchos retiros pendientes",
                "message": f"{metrics.get('pending_withdrawals_count', 0)} retiros esperando procesamiento",
                "priority": 4
            })
        
        if metrics.get('problematic_games', 0) > 5:
            health_score -= 10
            recommendations.append({
                "title": "Revisar juegos problemáticos",
                "description": f"Hay {metrics.get('problematic_games', 0)} juegos sin actividad",
                "impact": "medio",
                "action": "Revisar y finalizar juegos inactivos"
            })
        
        return {
            "health_status": "bueno" if health_score >= 70 else "preocupante" if health_score >= 50 else "crítico",
            "health_score": health_score,
            "summary": "Análisis básico del sistema (IA no disponible)",
            "alerts": alerts[:3],
            "recommendations": recommendations[:5],
            "predictions": {
                "revenue_next_week": "No disponible sin IA",
                "user_growth": "No disponible sin IA",
                "risks": []
            },
            "generated_at": timezone.now().isoformat(),
            "source": "fallback"
        }
    
    def _generate_basic_report(self, metrics: Dict[str, Any], report_type: str) -> str:
        """Genera reporte básico sin IA"""
        report = f"# Reporte {report_type.capitalize()} - {timezone.now().strftime('%Y-%m-%d')}\n\n"
        report += "## Resumen\n"
        report += f"Ingresos: ${metrics.get('platform_revenue', 0):.2f}\n"
        report += f"Usuarios activos: {metrics.get('active_users', 0)}\n"
        report += f"Juegos activos: {metrics.get('active_games', 0)}\n\n"
        report += "**Nota:** Reporte generado sin IA. Configura GEMINI_API_KEY para análisis avanzado."
        return report


# Instancia global del asistente
ai_assistant = BingoAIAssistant()

