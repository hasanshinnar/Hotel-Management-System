"""
Main Autonomous Booking Agent Orchestrator
Implements the perceive-reason-act cycle with continuous learning
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
from enum import Enum
import logging

from .perception import PerceptionLayer
from .reasoning import ReasoningEngine
from .action import ActionLayer
from ..analyzers.customer_analyzer import CustomerAnalyzer
from ..recommenders.upgrade_recommender import UpgradeRecommender
from ..resolvers.overbooking_resolver import OverbookingResolver
from ..integrations.watsonx_client import WatsonxClient
from ..utils.logger import AgentLogger
from ..utils.metrics import MetricsCollector


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    REASONING = "reasoning"
    ACTING = "acting"
    LEARNING = "learning"
    ERROR = "error"


@dataclass
class AgentContext:
    """Context for agent decision-making"""
    customer_id: str
    booking_id: Optional[str]
    current_state: AgentState
    confidence_score: float
    metadata: Dict[str, Any]
    timestamp: datetime


class AutonomousBookingAgent:
    """
    Main orchestrator for the autonomous booking agent.
    Implements the perceive-reason-act cycle with continuous learning.
    
    Based on IBM watsonx.ai principles:
    - Foundation models for intelligent decision-making
    - Governance and trust through explainable AI
    - Continuous learning from outcomes
    """
    
    def __init__(
        self,
        db_session,
        watsonx_client: WatsonxClient,
        config: Dict[str, Any]
    ):
        self.db = db_session
        self.watsonx = watsonx_client
        self.config = config
        self.logger = AgentLogger("AutonomousAgent")
        self.metrics = MetricsCollector()
        
        # Initialize layers
        self.perception = PerceptionLayer(db_session, watsonx_client)
        self.reasoning = ReasoningEngine(config)
        self.action = ActionLayer(db_session)
        
        # Initialize specialized components
        self.customer_analyzer = CustomerAnalyzer(db_session, watsonx_client)
        self.upgrade_recommender = UpgradeRecommender(db_session)
        self.overbooking_resolver = OverbookingResolver(db_session)
        
        self.state = AgentState.IDLE
        self.logger.info("Autonomous Booking Agent initialized")
        
    async def process_booking_request(
        self,
        customer_id: str,
        booking_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main entry point for processing booking requests.
        Implements the full perceive-reason-act cycle.
        
        Args:
            customer_id: Unique customer identifier
            booking_params: Booking parameters (dates, room type, etc.)
            
        Returns:
            Dict containing booking result, recommendations, and explanations
        """
        context = AgentContext(
            customer_id=customer_id,
            booking_id=None,
            current_state=AgentState.ANALYZING,
            confidence_score=0.0,
            metadata={},
            timestamp=datetime.utcnow()
        )
        
        try:
            self.logger.info(f"Processing booking request for customer {customer_id}")
            
            # PERCEIVE: Gather all relevant information
            self.state = AgentState.ANALYZING
            perception_data = await self._perceive(customer_id, booking_params)
            
            # REASON: Make intelligent decisions
            self.state = AgentState.REASONING
            decisions = await self._reason(perception_data, context)
            
            # ACT: Execute decisions
            self.state = AgentState.ACTING
            results = await self._act(decisions, context)
            
            # LEARN: Update models based on outcomes
            self.state = AgentState.LEARNING
            await self._learn(perception_data, decisions, results)
            
            self.state = AgentState.IDLE
            
            return {
                "success": True,
                "booking_id": results.get("booking_id"),
                "recommendations": results.get("recommendations", []),
                "confidence": context.confidence_score,
                "explanation": results.get("explanation"),
                "metadata": {
                    "processing_time_ms": (
                        datetime.utcnow() - context.timestamp
                    ).total_seconds() * 1000,
                    "agent_version": self.config.get("version", "1.0.0")
                }
            }
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Agent processing failed: {str(e)}", exc_info=True)
            self.metrics.record_error("booking_processing", str(e))
            
            return {
                "success": False,
                "error": str(e),
                "fallback_action": "human_intervention_required",
                "escalation_priority": self._calculate_escalation_priority(e)
            }
    
    async def _perceive(
        self,
        customer_id: str,
        booking_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perception phase: Gather and process all relevant information
        
        Collects data from multiple sources in parallel:
        - Customer profile and history
        - Room availability and pricing
        - Market conditions
        - Customer sentiment
        """
        self.logger.info(f"Perceiving data for customer {customer_id}")
        
        # Parallel data collection for efficiency
        tasks = [
            self.perception.get_customer_profile(customer_id),
            self.perception.get_booking_history(customer_id),
            self.perception.get_room_availability(booking_params),
            self.perception.get_market_conditions(booking_params),
            self.perception.get_customer_sentiment(customer_id)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any errors in data collection
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Data collection task {i} failed: {result}")
                results[i] = {}  # Use empty dict as fallback
        
        return {
            "customer_profile": results[0],
            "booking_history": results[1],
            "room_availability": results[2],
            "market_conditions": results[3],
            "customer_sentiment": results[4],
            "timestamp": datetime.utcnow()
        }
    
    async def _reason(
        self,
        perception_data: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Reasoning phase: Make intelligent decisions based on perceived data
        
        Uses multiple AI techniques:
        - Customer segmentation and analysis
        - Predictive modeling
        - Optimization algorithms
        - Rule-based logic
        """
        self.logger.info("Reasoning about optimal actions")
        
        # Customer analysis
        customer_insights = await self.customer_analyzer.analyze(
            perception_data["customer_profile"],
            perception_data["booking_history"]
        )
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            customer_insights,
            perception_data
        )
        
        # Check for conflicts
        conflicts = await self._detect_conflicts(perception_data)
        
        # Optimize booking
        optimal_booking = await self.reasoning.optimize_booking(
            perception_data,
            customer_insights,
            recommendations
        )
        
        # Calculate confidence
        context.confidence_score = self._calculate_confidence(
            customer_insights,
            optimal_booking,
            conflicts
        )
        
        return {
            "customer_insights": customer_insights,
            "recommendations": recommendations,
            "conflicts": conflicts,
            "optimal_booking": optimal_booking,
            "confidence": context.confidence_score
        }
    
    async def _act(
        self,
        decisions: Dict[str, Any],
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Action phase: Execute decisions and handle conflicts
        
        Executes in order:
        1. Resolve any conflicts
        2. Create booking
        3. Apply recommendations
        4. Send notifications
        5. Generate explanation
        """
        self.logger.info("Executing agent decisions")
        
        results = {}
        
        # Handle conflicts first
        if decisions["conflicts"]:
            conflict_resolution = await self._resolve_conflicts(
                decisions["conflicts"]
            )
            results["conflict_resolution"] = conflict_resolution
            
            # Escalate if needed
            if conflict_resolution.get("human_intervention_needed"):
                results["escalated"] = True
                return results
        
        # Execute booking
        booking_result = await self.action.create_booking(
            decisions["optimal_booking"]
        )
        results["booking_id"] = booking_result["booking_id"]
        context.booking_id = booking_result["booking_id"]
        
        # Apply recommendations
        if decisions["recommendations"]:
            recommendation_results = await self.action.apply_recommendations(
                booking_result["booking_id"],
                decisions["recommendations"]
            )
            results["recommendations"] = recommendation_results
        
        # Send notifications
        await self.action.send_notifications(
            context.customer_id,
            booking_result,
            decisions["recommendations"]
        )
        
        # Generate explanation using LLM
        results["explanation"] = await self._generate_explanation(
            decisions,
            results
        )
        
        # Record audit trail
        await self._record_audit_trail(context, decisions, results)
        
        return results
    
    async def _learn(
        self,
        perception_data: Dict[str, Any],
        decisions: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """
        Learning phase: Update models based on outcomes
        
        Implements continuous learning:
        - Records metrics for monitoring
        - Updates customer profiles
        - Triggers model retraining if needed
        """
        self.logger.info("Learning from booking outcome")
        
        # Record metrics
        self.metrics.record_booking_success(
            results.get("booking_id"),
            decisions["confidence"]
        )
        
        # Update customer profile with new booking
        if results.get("booking_id"):
            await self.customer_analyzer.update_profile(
                perception_data["customer_profile"]["customer_id"],
                results
            )
        
        # Check if models need retraining
        if self.metrics.should_retrain():
            self.logger.info("Triggering model retraining")
            await self._retrain_models()
    
    async def _generate_recommendations(
        self,
        customer_insights: Dict[str, Any],
        perception_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Room upgrade recommendations
        if customer_insights.get("upgrade_propensity", 0) > 0.7:
            upgrade_recs = await self.upgrade_recommender.suggest_upgrades(
                customer_insights,
                perception_data["room_availability"]
            )
            recommendations.extend(upgrade_recs)
        
        # Service recommendations (spa, dining, etc.)
        service_recs = await self._recommend_services(customer_insights)
        recommendations.extend(service_recs)
        
        # Loyalty program recommendations
        if customer_insights.get("loyalty_tier") in ["gold", "platinum"]:
            loyalty_recs = await self._recommend_loyalty_benefits(
                customer_insights
            )
            recommendations.extend(loyalty_recs)
        
        return recommendations
    
    async def _detect_conflicts(
        self,
        perception_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect potential conflicts (overbooking, pricing issues, etc.)"""
        conflicts = []
        
        # Check for overbooking risk
        if perception_data["room_availability"]["occupancy_rate"] > 0.95:
            overbooking_risk = await self.overbooking_resolver.assess_risk(
                perception_data
            )
            if overbooking_risk["risk_level"] in ["high", "critical"]:
                conflicts.append({
                    "type": "overbooking",
                    "severity": overbooking_risk["risk_level"],
                    "data": overbooking_risk
                })
        
        # Check for pricing conflicts
        market_price = perception_data["market_conditions"].get("avg_price", 0)
        our_price = perception_data["room_availability"].get("current_price", 0)
        
        if market_price > 0 and abs(market_price - our_price) / market_price > 0.2:
            conflicts.append({
                "type": "pricing_mismatch",
                "severity": "medium",
                "data": {
                    "market_price": market_price,
                    "our_price": our_price,
                    "difference_pct": abs(market_price - our_price) / market_price * 100
                }
            })
        
        return conflicts
    
    async def _resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Autonomously resolve conflicts"""
        resolutions = []
        
        for conflict in conflicts:
            if conflict["type"] == "overbooking":
                resolution = await self.overbooking_resolver.resolve(
                    conflict["data"]
                )
                resolutions.append(resolution)
            
            elif conflict["type"] == "pricing_mismatch":
                resolution = await self._resolve_pricing_conflict(
                    conflict["data"]
                )
                resolutions.append(resolution)
        
        return {
            "conflicts_resolved": len(resolutions),
            "resolutions": resolutions,
            "human_intervention_needed": any(
                r.get("escalate", False) for r in resolutions
            )
        }
    
    def _calculate_confidence(
        self,
        customer_insights: Dict[str, Any],
        optimal_booking: Dict[str, Any],
        conflicts: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for decisions"""
        base_confidence = 0.8
        
        # Adjust based on customer data quality
        data_completeness = customer_insights.get("data_completeness", 0.5)
        if data_completeness < 0.5:
            base_confidence -= 0.2
        
        # Adjust based on conflicts
        if conflicts:
            severity_penalty = {
                "low": 0.05,
                "medium": 0.1,
                "high": 0.2,
                "critical": 0.3
            }
            for conflict in conflicts:
                base_confidence -= severity_penalty.get(
                    conflict.get("severity", "medium"),
                    0.1
                )
        
        # Adjust based on model predictions
        if optimal_booking.get("prediction_confidence"):
            base_confidence = (
                base_confidence * 0.7 +
                optimal_booking["prediction_confidence"] * 0.3
            )
        
        return max(0.0, min(1.0, base_confidence))
    
    async def _generate_explanation(
        self,
        decisions: Dict[str, Any],
        results: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation using LLM"""
        
        prompt = f"""
        Generate a clear, customer-friendly explanation for the following booking decision:
        
        Customer Segment: {decisions['customer_insights'].get('segment', 'Regular')}
        Loyalty Tier: {decisions['customer_insights'].get('loyalty_tier', 'bronze')}
        Recommendations Offered: {len(decisions['recommendations'])}
        Conflicts Resolved: {len(results.get('conflict_resolution', {}).get('resolutions', []))}
        Confidence Level: {decisions['confidence']:.0%}
        
        Explain in 2-3 sentences why these decisions benefit the customer.
        Be warm, professional, and highlight the value provided.
        """
        
        try:
            explanation = await self.watsonx.generate_text(
                prompt=prompt,
                max_tokens=150,
                temperature=0.7
            )
            return explanation
        except Exception as e:
            self.logger.error(f"Failed to generate explanation: {e}")
            return "Your booking has been optimized based on your preferences and our current availability."
    
    async def _recommend_services(
        self,
        customer_insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend additional services"""
        # Placeholder - would integrate with service recommendation engine
        return []
    
    async def _recommend_loyalty_benefits(
        self,
        customer_insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recommend loyalty program benefits"""
        # Placeholder - would integrate with loyalty system
        return []
    
    async def _resolve_pricing_conflict(
        self,
        conflict_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve pricing mismatch"""
        # Simple resolution: adjust to market average
        market_price = conflict_data["market_price"]
        our_price = conflict_data["our_price"]
        adjusted_price = (market_price + our_price) / 2
        
        return {
            "type": "pricing_adjustment",
            "original_price": our_price,
            "adjusted_price": adjusted_price,
            "reason": "Market alignment",
            "escalate": False
        }
    
    async def _record_audit_trail(
        self,
        context: AgentContext,
        decisions: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """Record complete audit trail for compliance"""
        audit_entry = {
            "timestamp": datetime.utcnow(),
            "customer_id": context.customer_id,
            "booking_id": context.booking_id,
            "agent_state": context.current_state.value,
            "confidence_score": context.confidence_score,
            "decisions": decisions,
            "results": results,
            "metadata": context.metadata
        }
        
        # Store in audit log
        # Implementation would write to database or logging system
        self.logger.info(f"Audit trail recorded for booking {context.booking_id}")
    
    async def _retrain_models(self):
        """Trigger model retraining with new data"""
        self.logger.info("Initiating model retraining pipeline")
        # Implementation would trigger MLOps pipeline
        pass
    
    def _calculate_escalation_priority(self, error: Exception) -> str:
        """Calculate priority for human escalation"""
        # Simple heuristic - would be more sophisticated in production
        error_str = str(error).lower()
        
        if any(word in error_str for word in ["payment", "fraud", "security"]):
            return "critical"
        elif any(word in error_str for word in ["overbooking", "conflict"]):
            return "high"
        else:
            return "medium"

# Made with Bob
