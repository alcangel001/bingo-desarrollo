"""
Asistente Inteligente Local para Administración
Sistema basado en reglas - sin APIs externas, siempre funciona
"""
import logging
import json
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone

logger = logging.getLogger(__name__)


class SmartAssistant:
    """Asistente inteligente local que analiza métricas y genera recomendaciones"""
    
    def __init__(self):
        self.is_available = True  # Siempre disponible
    
    def analyze_dashboard_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza las métricas del dashboard usando reglas inteligentes
        
        Args:
            metrics: Diccionario con todas las métricas del dashboard
            
        Returns:
            Dict con análisis, alertas y recomendaciones
        """
        try:
            # Calcular score de salud
            health_score = self._calculate_health_score(metrics)
            
            # Generar alertas
            alerts = self._generate_alerts(metrics)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(metrics)
            
            # Generar predicciones
            predictions = self._generate_predictions(metrics)
            
            # Determinar estado de salud
            if health_score >= 80:
                health_status = "bueno"
            elif health_score >= 60:
                health_status = "preocupante"
            else:
                health_status = "crítico"
            
            # Generar resumen
            summary = self._generate_summary(metrics, health_score, health_status)
            
            return {
                "health_status": health_status,
                "health_score": health_score,
                "summary": summary,
                "alerts": alerts[:3],  # Máximo 3 alertas
                "recommendations": recommendations[:5],  # Máximo 5 recomendaciones
                "predictions": predictions,
                "generated_at": timezone.now().isoformat(),
                "source": "smart_assistant"
            }
            
        except Exception as e:
            logger.error(f"Error en análisis inteligente: {str(e)}")
            return self._generate_basic_analysis(metrics)
    
    def answer_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Responde preguntas usando búsqueda inteligente en las métricas
        
        Args:
            question: Pregunta del usuario
            context: Contexto con métricas
            
        Returns:
            Dict con respuesta y acciones sugeridas
        """
        try:
            question_lower = question.lower()
            
            # Análisis de la pregunta
            answer = self._process_question(question_lower, context)
            
            return {
                "answer": answer["text"],
                "confidence": answer.get("confidence", 70),
                "sources": answer.get("sources", []),
                "suggested_actions": answer.get("actions", []),
                "timestamp": timezone.now().isoformat(),
                "source": "smart_assistant"
            }
            
        except Exception as e:
            logger.error(f"Error respondiendo pregunta: {str(e)}")
            return {
                "answer": f"Lo siento, hubo un error al procesar tu pregunta: {str(e)}",
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
        try:
            report = f"# Reporte {report_type.capitalize()} - {timezone.now().strftime('%Y-%m-%d')}\n\n"
            
            # Resumen ejecutivo
            report += "## Resumen Ejecutivo\n\n"
            report += f"- **Ingresos de plataforma:** ${metrics.get('platform_revenue', 0):.2f}\n"
            report += f"- **Balance del sistema:** ${metrics.get('system_balance', 0):.2f}\n"
            report += f"- **Usuarios activos:** {metrics.get('active_users', 0)}\n"
            report += f"- **Juegos activos:** {metrics.get('active_games', 0)}\n"
            report += f"- **Rifas activas:** {metrics.get('active_raffles', 0)}\n\n"
            
            # Métricas clave
            report += "## Métricas Clave\n\n"
            report += f"- **Usuarios registrados:** {metrics.get('registered_users', 0)}\n"
            report += f"- **Nuevos usuarios (7d):** {metrics.get('new_users_week', 0)}\n"
            report += f"- **Retiros pendientes:** {metrics.get('pending_withdrawals_count', 0)}\n"
            report += f"- **Liquidez total:** ${metrics.get('total_balance', 0):.2f}\n"
            report += f"- **Fondos en escrow:** ${metrics.get('total_escrow', 0):.2f}\n\n"
            
            # Alertas
            alerts = self._generate_alerts(metrics)
            if alerts:
                report += "## Alertas Importantes\n\n"
                for alert in alerts[:3]:
                    report += f"- **{alert['title']}:** {alert['message']}\n"
                report += "\n"
            
            # Recomendaciones
            recommendations = self._generate_recommendations(metrics)
            if recommendations:
                report += "## Recomendaciones\n\n"
                for rec in recommendations[:5]:
                    report += f"- **{rec['title']}:** {rec['description']}\n"
                    report += f"  *Acción:* {rec['action']}\n\n"
            
            # Próximos pasos
            report += "## Próximos Pasos\n\n"
            if metrics.get('pending_withdrawals_count', 0) > 0:
                report += f"- Procesar {metrics.get('pending_withdrawals_count', 0)} retiros pendientes\n"
            if metrics.get('problematic_games', 0) > 0:
                report += f"- Revisar {metrics.get('problematic_games', 0)} juegos con problemas\n"
            if metrics.get('system_balance', 0) < 0:
                report += "- Revisar balance negativo del sistema\n"
            else:
                report += "- Monitorear métricas diariamente\n"
                report += "- Revisar usuarios de alto saldo\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
            return self._generate_basic_report(metrics, report_type)
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> int:
        """Calcula un score de salud del sistema (0-100)"""
        score = 100
        
        # Penalizar balance negativo
        if metrics.get('system_balance', 0) < 0:
            score -= 30
        
        # Penalizar muchos retiros pendientes
        pending = metrics.get('pending_withdrawals_count', 0)
        if pending > 20:
            score -= 20
        elif pending > 10:
            score -= 10
        
        # Penalizar juegos problemáticos
        problematic = metrics.get('problematic_games', 0)
        if problematic > 10:
            score -= 15
        elif problematic > 5:
            score -= 8
        
        # Penalizar transacciones sospechosas
        suspicious = metrics.get('suspicious_transactions', 0)
        if suspicious > 5:
            score -= 10
        
        # Penalizar baja liquidez
        liquidity_ratio = metrics.get('liquidity_ratio', 100)
        if liquidity_ratio < 30:
            score -= 15
        elif liquidity_ratio < 50:
            score -= 8
        
        # Bonus por buen crecimiento
        new_users = metrics.get('new_users_week', 0)
        if new_users > 10:
            score += 5
        
        return max(0, min(100, score))
    
    def _generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera alertas basadas en métricas"""
        alerts = []
        
        # Alerta de balance negativo
        if metrics.get('system_balance', 0) < 0:
            alerts.append({
                "type": "error",
                "title": "Balance del Sistema Negativo",
                "message": f"El sistema tiene balance negativo de ${abs(metrics.get('system_balance', 0)):.2f}",
                "priority": 5
            })
        
        # Alerta de muchos retiros pendientes
        pending = metrics.get('pending_withdrawals_count', 0)
        if pending > 20:
            alerts.append({
                "type": "warning",
                "title": "Muchos Retiros Pendientes",
                "message": f"Hay {pending} retiros esperando procesamiento. Total: ${metrics.get('pending_withdrawals', 0):.2f}",
                "priority": 4
            })
        
        # Alerta de juegos problemáticos
        problematic = metrics.get('problematic_games', 0)
        if problematic > 5:
            alerts.append({
                "type": "warning",
                "title": "Juegos Sin Actividad",
                "message": f"{problematic} juegos sin actividad en las últimas 24 horas. Considera finalizarlos.",
                "priority": 3
            })
        
        # Alerta de transacciones sospechosas
        suspicious = metrics.get('suspicious_transactions', 0)
        if suspicious > 0:
            alerts.append({
                "type": "info",
                "title": "Transacciones Sospechosas",
                "message": f"Se detectaron {suspicious} transacciones sospechosas que requieren revisión.",
                "priority": 4
            })
        
        # Alerta de liquidez baja
        liquidity_ratio = metrics.get('liquidity_ratio', 100)
        if liquidity_ratio < 30:
            alerts.append({
                "type": "warning",
                "title": "Liquidez Baja",
                "message": f"El ratio de liquidez es {liquidity_ratio:.1f}%. Considera revisar fondos retenidos.",
                "priority": 3
            })
        
        # Ordenar por prioridad
        alerts.sort(key=lambda x: x['priority'], reverse=True)
        return alerts
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera recomendaciones inteligentes"""
        recommendations = []
        
        # Recomendación de procesar retiros
        pending = metrics.get('pending_withdrawals_count', 0)
        if pending > 10:
            recommendations.append({
                "title": "Procesar Retiros Pendientes",
                "description": f"Hay {pending} retiros pendientes que requieren atención inmediata.",
                "impact": "alto",
                "action": f"Ir a Procesar Retiros y revisar las {pending} solicitudes pendientes"
            })
        
        # Recomendación de revisar juegos
        problematic = metrics.get('problematic_games', 0)
        if problematic > 0:
            recommendations.append({
                "title": "Revisar Juegos Inactivos",
                "description": f"{problematic} juegos no tienen actividad reciente. Considera finalizarlos para liberar fondos.",
                "impact": "medio",
                "action": "Revisar juegos activos y finalizar aquellos sin actividad"
            })
        
        # Recomendación de crecimiento
        new_users = metrics.get('new_users_week', 0)
        if new_users < 5:
            recommendations.append({
                "title": "Estrategia de Crecimiento",
                "description": f"Solo {new_users} nuevos usuarios esta semana. Considera promociones o marketing.",
                "impact": "medio",
                "action": "Crear promociones o campañas para atraer más usuarios"
            })
        
        # Recomendación de diversificación
        active_games = metrics.get('active_games', 0)
        active_raffles = metrics.get('active_raffles', 0)
        if active_games > 0 and active_raffles == 0:
            recommendations.append({
                "title": "Diversificar Eventos",
                "description": "Solo hay juegos activos. Considera crear rifas para diversificar ingresos.",
                "impact": "bajo",
                "action": "Crear una rifa para ofrecer más opciones a los usuarios"
            })
        
        # Recomendación de seguridad
        suspicious = metrics.get('suspicious_transactions', 0)
        if suspicious > 0:
            recommendations.append({
                "title": "Revisar Seguridad",
                "description": f"Se detectaron {suspicious} transacciones sospechosas.",
                "impact": "alto",
                "action": "Revisar transacciones y usuarios con actividad sospechosa"
            })
        
        # Recomendación de usuarios de alto saldo
        high_balance = metrics.get('high_balance_users', 0)
        if high_balance > 5:
            recommendations.append({
                "title": "Revisar Usuarios de Alto Saldo",
                "description": f"{high_balance} usuarios tienen saldos superiores a $1000.",
                "impact": "medio",
                "action": "Revisar estos usuarios para asegurar que las transacciones son legítimas"
            })
        
        # Ordenar por impacto
        recommendations.sort(key=lambda x: {"alto": 3, "medio": 2, "bajo": 1}.get(x['impact'], 0), reverse=True)
        return recommendations
    
    def _generate_predictions(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Genera predicciones basadas en tendencias"""
        predictions = {}
        
        # Predicción de ingresos
        daily_income = metrics.get('daily_income', 0)
        if daily_income > 0:
            weekly_prediction = daily_income * 7
            predictions["revenue_next_week"] = f"${weekly_prediction:.2f} (basado en tendencia actual)"
        else:
            predictions["revenue_next_week"] = "No disponible (datos insuficientes)"
        
        # Predicción de crecimiento
        new_users = metrics.get('new_users_week', 0)
        if new_users > 0:
            growth_rate = new_users / max(metrics.get('registered_users', 1), 1) * 100
            predictions["user_growth"] = f"{growth_rate:.1f}% semanal (basado en últimos 7 días)"
        else:
            predictions["user_growth"] = "Sin crecimiento reciente"
        
        # Riesgos
        risks = []
        if metrics.get('system_balance', 0) < 0:
            risks.append("Balance negativo del sistema")
        if metrics.get('pending_withdrawals_count', 0) > 20:
            risks.append("Alto volumen de retiros pendientes")
        if metrics.get('liquidity_ratio', 100) < 30:
            risks.append("Baja liquidez del sistema")
        if metrics.get('suspicious_transactions', 0) > 5:
            risks.append("Transacciones sospechosas detectadas")
        
        predictions["risks"] = risks if risks else ["No se detectaron riesgos significativos"]
        
        return predictions
    
    def _generate_summary(self, metrics: Dict[str, Any], health_score: int, health_status: str) -> str:
        """Genera un resumen del estado del sistema con análisis más profundo"""
        summary_parts = []
        
        # Análisis más contextual
        if health_status == "bueno":
            summary_parts.append("El sistema está funcionando correctamente y de manera estable.")
        elif health_status == "preocupante":
            summary_parts.append("El sistema requiere atención en algunas áreas para mantener un rendimiento óptimo.")
        else:
            summary_parts.append("El sistema tiene problemas críticos que requieren acción inmediata para evitar impactos mayores.")
        
        # Agregar métricas clave con contexto
        active_games = metrics.get('active_games', 0)
        active_users = metrics.get('active_users', 0)
        platform_revenue = metrics.get('platform_revenue', 0)
        new_users = metrics.get('new_users_week', 0)
        pending_withdrawals = metrics.get('pending_withdrawals_count', 0)
        
        summary_parts.append(f"Actualmente hay {active_games} juegos activos, {active_users} usuarios activos en los últimos 7 días, y los ingresos de plataforma son ${platform_revenue:.2f}.")
        
        # Agregar contexto adicional
        if new_users > 0:
            summary_parts.append(f"Esta semana se registraron {new_users} nuevos usuarios, lo que indica crecimiento.")
        
        if pending_withdrawals > 0:
            summary_parts.append(f"Hay {pending_withdrawals} retiros pendientes que requieren procesamiento.")
        
        # Agregar alerta principal si existe
        alerts = self._generate_alerts(metrics)
        if alerts:
            main_alert = alerts[0]
            summary_parts.append(f"Alerta principal: {main_alert['title']} - {main_alert['message']}")
        
        # Análisis de tendencias
        system_balance = metrics.get('system_balance', 0)
        if system_balance > 0:
            summary_parts.append("El balance del sistema es positivo, lo que indica estabilidad financiera.")
        elif system_balance < 0:
            summary_parts.append("⚠️ El balance del sistema es negativo, lo que requiere atención inmediata.")
        
        return " ".join(summary_parts)
    
    def _process_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Procesa preguntas usando búsqueda inteligente"""
        context = context or {}
        answer_data = {
            "text": "",
            "confidence": 70,
            "sources": [],
            "actions": []
        }
        
        # Análisis de preguntas comunes
        if any(word in question for word in ["estado", "salud", "sistema", "como esta"]):
            health_score = self._calculate_health_score(context)
            if health_score >= 80:
                status = "excelente"
            elif health_score >= 60:
                status = "bueno"
            else:
                status = "requiere atención"
            
            answer_data["text"] = f"El estado del sistema es {status} (score: {health_score}/100). "
            answer_data["text"] += f"Tienes {context.get('active_games', 0)} juegos activos, "
            answer_data["text"] += f"{context.get('active_users', 0)} usuarios activos, "
            answer_data["text"] += f"y el balance del sistema es ${context.get('system_balance', 0):.2f}."
            answer_data["confidence"] = 85
            answer_data["sources"] = ["health_score", "active_games", "active_users", "system_balance"]
        
        elif any(word in question for word in ["usuario", "usuarios", "cuantos usuarios"]):
            registered = context.get('registered_users', 0)
            active = context.get('active_users', 0)
            new_week = context.get('new_users_week', 0)
            
            answer_data["text"] = f"Tienes {registered} usuarios registrados en total. "
            answer_data["text"] += f"De estos, {active} están activos (últimos 7 días). "
            answer_data["text"] += f"Esta semana se registraron {new_week} nuevos usuarios."
            answer_data["confidence"] = 90
            answer_data["sources"] = ["registered_users", "active_users", "new_users_week"]
        
        elif any(word in question for word in ["ingreso", "ingresos", "revenue", "dinero", "ganancia"]):
            revenue = context.get('platform_revenue', 0)
            balance = context.get('system_balance', 0)
            daily = context.get('daily_income', 0)
            
            answer_data["text"] = f"Los ingresos totales de la plataforma son ${revenue:.2f}. "
            answer_data["text"] += f"El balance del sistema es ${balance:.2f}. "
            if daily > 0:
                answer_data["text"] += f"El ingreso diario promedio es ${daily:.2f}."
            answer_data["confidence"] = 85
            answer_data["sources"] = ["platform_revenue", "system_balance", "daily_income"]
            answer_data["actions"] = ["Revisar transacciones recientes", "Ver reporte de ingresos"]
        
        elif any(word in question for word in ["juego", "juegos", "bingo"]):
            active = context.get('active_games', 0)
            problematic = context.get('problematic_games', 0)
            
            answer_data["text"] = f"Actualmente hay {active} juegos activos. "
            if problematic > 0:
                answer_data["text"] += f"⚠️ {problematic} juegos tienen problemas (sin actividad reciente). "
                answer_data["actions"] = [f"Revisar {problematic} juegos problemáticos"]
            else:
                answer_data["text"] += "Todos los juegos están funcionando correctamente."
            answer_data["confidence"] = 80
            answer_data["sources"] = ["active_games", "problematic_games"]
        
        elif any(word in question for word in ["retiro", "retiros", "solicitud"]):
            pending = context.get('pending_withdrawals_count', 0)
            amount = context.get('pending_withdrawals', 0)
            
            if pending > 0:
                answer_data["text"] = f"Hay {pending} retiros pendientes de procesamiento por un total de ${amount:.2f}. "
                answer_data["text"] += "Estos requieren tu atención para mantener la satisfacción de los usuarios."
                answer_data["actions"] = [f"Procesar {pending} retiros pendientes"]
            else:
                answer_data["text"] = "No hay retiros pendientes. Todo está al día."
            answer_data["confidence"] = 90
            answer_data["sources"] = ["pending_withdrawals_count", "pending_withdrawals"]
        
        elif any(word in question for word in ["problema", "problemas", "alerta", "alertas"]):
            alerts = self._generate_alerts(context)
            if alerts:
                answer_data["text"] = f"Se detectaron {len(alerts)} alertas importantes: "
                for i, alert in enumerate(alerts[:3], 1):
                    answer_data["text"] += f"{i}. {alert['title']}: {alert['message']}. "
                answer_data["confidence"] = 85
            else:
                answer_data["text"] = "No hay alertas críticas en este momento. El sistema funciona correctamente."
                answer_data["confidence"] = 80
            answer_data["sources"] = ["alerts"]
        
        elif any(word in question for word in ["recomendacion", "recomendaciones", "sugerencia"]):
            recommendations = self._generate_recommendations(context)
            if recommendations:
                answer_data["text"] = f"Tengo {len(recommendations)} recomendaciones para ti: "
                for i, rec in enumerate(recommendations[:3], 1):
                    answer_data["text"] += f"{i}. {rec['title']}: {rec['description']} "
                answer_data["confidence"] = 80
            else:
                answer_data["text"] = "El sistema está funcionando bien. No hay recomendaciones urgentes en este momento."
                answer_data["confidence"] = 70
            answer_data["sources"] = ["recommendations"]
        
        elif any(word in question for word in ["analisis", "análisis", "analizar", "metricas", "métricas", "analisis de metricas", "análisis de métricas"]):
            # Análisis completo de métricas
            health_score = self._calculate_health_score(context)
            if health_score >= 80:
                health_status = "excelente"
            elif health_score >= 60:
                health_status = "bueno"
            else:
                health_status = "requiere atención"
            
            # Generar análisis completo
            analysis_parts = []
            analysis_parts.append("📊 ANÁLISIS COMPLETO DE MÉTRICAS\n\n")
            
            # Estado general
            analysis_parts.append(f"Estado del Sistema: {health_status.upper()} (Score: {health_score}/100)\n\n")
            
            # Métricas financieras
            analysis_parts.append("💰 MÉTRICAS FINANCIERAS:\n")
            analysis_parts.append(f"• Ingresos de plataforma: ${context.get('platform_revenue', 0):.2f}\n")
            analysis_parts.append(f"• Balance del sistema: ${context.get('system_balance', 0):.2f}\n")
            analysis_parts.append(f"• Entradas diarias: ${context.get('daily_income', 0):.2f}\n")
            analysis_parts.append(f"• Salidas diarias: ${context.get('daily_expenses', 0):.2f}\n")
            analysis_parts.append(f"• Liquidez total: ${context.get('total_balance', 0):.2f}\n")
            analysis_parts.append(f"• Fondos en escrow: ${context.get('total_escrow', 0):.2f}\n\n")
            
            # Métricas de usuarios
            analysis_parts.append("👥 MÉTRICAS DE USUARIOS:\n")
            analysis_parts.append(f"• Usuarios registrados: {context.get('registered_users', 0)}\n")
            analysis_parts.append(f"• Usuarios activos (7d): {context.get('active_users', 0)}\n")
            analysis_parts.append(f"• Nuevos usuarios (7d): {context.get('new_users_week', 0)}\n")
            analysis_parts.append(f"• Usuarios bloqueados: {context.get('blocked_users', 0)}\n")
            analysis_parts.append(f"• Usuarios de alto saldo (>$1000): {context.get('high_balance_users', 0)}\n\n")
            
            # Métricas de actividad
            analysis_parts.append("🎮 MÉTRICAS DE ACTIVIDAD:\n")
            analysis_parts.append(f"• Juegos activos: {context.get('active_games', 0)}\n")
            analysis_parts.append(f"• Juegos con problemas: {context.get('problematic_games', 0)}\n")
            analysis_parts.append(f"• Rifas activas: {context.get('active_raffles', 0)}\n\n")
            
            # Retiros
            analysis_parts.append("💸 RETIROS:\n")
            analysis_parts.append(f"• Pendientes: {context.get('pending_withdrawals_count', 0)} (${context.get('pending_withdrawals', 0):.2f})\n")
            analysis_parts.append(f"• Tiempo promedio: {context.get('avg_withdrawal_hours', 0):.1f} horas\n")
            analysis_parts.append(f"• Tasa de aprobación: {context.get('approval_ratio', 0):.1f}%\n\n")
            
            # Alertas
            alerts = self._generate_alerts(context)
            if alerts:
                analysis_parts.append("⚠️ ALERTAS DETECTADAS:\n")
                for i, alert in enumerate(alerts[:3], 1):
                    analysis_parts.append(f"{i}. {alert['title']}: {alert['message']}\n")
                analysis_parts.append("\n")
            
            # Recomendaciones
            recommendations = self._generate_recommendations(context)
            if recommendations:
                analysis_parts.append("💡 RECOMENDACIONES:\n")
                for i, rec in enumerate(recommendations[:3], 1):
                    impact_emoji = "🔴" if rec['impact'] == 'alto' else "🟡" if rec['impact'] == 'medio' else "🟢"
                    analysis_parts.append(f"{i}. {impact_emoji} {rec['title']}: {rec['description']}\n")
                analysis_parts.append("\n")
            
            answer_data["text"] = "".join(analysis_parts)
            answer_data["confidence"] = 95
            answer_data["sources"] = ["health_score", "platform_revenue", "system_balance", "registered_users", 
                                     "active_users", "active_games", "pending_withdrawals_count", "alerts", "recommendations"]
            if alerts:
                answer_data["actions"] = [f"Revisar {len(alerts)} alertas"]
            if recommendations:
                answer_data["actions"].extend([f"Atender recomendación: {rec['title']}" for rec in recommendations[:2]])
        
        else:
            # Respuesta inteligente basada en contexto
            answer_data = self._generate_contextual_response(question, context)
        
        return answer_data
    
    def _generate_basic_analysis(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Genera análisis básico sin IA"""
        return {
            "health_status": "preocupante",
            "health_score": 50,
            "summary": "Análisis básico disponible",
            "alerts": [],
            "recommendations": [],
            "predictions": {
                "revenue_next_week": "No disponible",
                "user_growth": "No disponible",
                "risks": []
            },
            "generated_at": timezone.now().isoformat(),
            "source": "fallback"
        }
    
    def _generate_basic_report(self, metrics: Dict[str, Any], report_type: str) -> str:
        """Genera reporte básico"""
        report = f"# Reporte {report_type.capitalize()} - {timezone.now().strftime('%Y-%m-%d')}\n\n"
        report += "## Resumen\n"
        report += f"Ingresos: ${metrics.get('platform_revenue', 0):.2f}\n"
        report += f"Usuarios activos: {metrics.get('active_users', 0)}\n"
        report += f"Juegos activos: {metrics.get('active_games', 0)}\n"
        return report
    
    def _generate_contextual_response(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera respuesta contextual e inteligente basada en el estado del sistema"""
        answer_data = {
            "text": "",
            "confidence": 65,
            "sources": [],
            "actions": []
        }
        
        # Analizar el estado general para dar contexto
        health_score = self._calculate_health_score(context)
        alerts = self._generate_alerts(context)
        recommendations = self._generate_recommendations(context)
        
        # Detectar si hay problemas críticos
        has_critical_issues = health_score < 60 or any(a['priority'] >= 4 for a in alerts)
        
        # Generar respuesta contextual
        if has_critical_issues:
            answer_data["text"] = "Veo que hay aspectos que requieren atención inmediata. "
            answer_data["text"] += f"El sistema tiene un score de salud de {health_score}/100. "
            
            if alerts:
                main_alert = alerts[0]
                answer_data["text"] += f"La alerta más importante es: {main_alert['title']}. "
                answer_data["text"] += f"{main_alert['message']} "
            
            if recommendations:
                answer_data["text"] += f"Te recomiendo: {recommendations[0]['title']}. "
            
            answer_data["text"] += "¿Quieres que te ayude con algo específico? Puedo darte más detalles sobre: estado del sistema, usuarios, ingresos, juegos, retiros, alertas o recomendaciones."
            answer_data["confidence"] = 75
            answer_data["sources"] = ["health_score", "alerts", "recommendations"]
            answer_data["actions"] = [
                "Pregunta: '¿qué problemas hay?'",
                "Pregunta: 'análisis de métricas'",
                f"Pregunta: '¿cómo soluciono {alerts[0]['title'] if alerts else 'esto'}?'"
            ]
        else:
            # Sistema saludable - respuesta más positiva
            answer_data["text"] = f"¡Excelente! El sistema está funcionando bien. "
            answer_data["text"] += f"Tienes un score de salud de {health_score}/100. "
            
            # Mencionar métricas positivas
            active_games = context.get('active_games', 0)
            active_users = context.get('active_users', 0)
            revenue = context.get('platform_revenue', 0)
            
            if active_games > 0:
                answer_data["text"] += f"Actualmente hay {active_games} juegos activos. "
            if active_users > 0:
                answer_data["text"] += f"Tienes {active_users} usuarios activos esta semana. "
            if revenue > 0:
                answer_data["text"] += f"Los ingresos de plataforma son ${revenue:.2f}. "
            
            answer_data["text"] += "¿En qué puedo ayudarte? Puedo darte información sobre: estado del sistema, análisis de métricas, usuarios, ingresos, juegos, retiros, alertas o recomendaciones."
            answer_data["confidence"] = 70
            answer_data["sources"] = ["health_score", "active_games", "active_users", "platform_revenue"]
            answer_data["actions"] = [
                "Pregunta: 'análisis de métricas'",
                "Pregunta: '¿cuántos usuarios hay?'",
                "Pregunta: '¿cuáles son los ingresos?'"
            ]
        
        return answer_data


# Instancia global del asistente inteligente
smart_assistant = SmartAssistant()


