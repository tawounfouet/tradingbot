"""
Strategy router for handling strategy-related API endpoints.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from tradingbot.core.exceptions import BusinessLogicError, NotFoundError, ValidationError
from tradingbot.dependencies.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from tradingbot.models.user import User
from pydantic import BaseModel
from tradingbot.schemas.common import BaseResponse
from tradingbot.schemas.strategy import (
    StrategyCreate,
    StrategyDeploymentCreate,
    StrategyDeploymentResponse,
    StrategyListResponse,
    StrategyResponse,
    StrategyUpdate,
)
from tradingbot.services.market_data_service import MarketDataService
from tradingbot.services.strategy_service import StrategyService

# Generic data response model
T = TypeVar("T")


class DataResponse(BaseResponse, Generic[T]):
    """Generic response wrapper with data field."""

    data: T


# Create router
router = APIRouter(prefix="/strategies", tags=["strategies"])


# Initialize services (will be dependency injected)
def get_strategy_service() -> StrategyService:
    """Get strategy service instance."""
    market_data_service = (
        MarketDataService()
    )  # This would be dependency injected in real app
    return StrategyService(market_data_service)


@router.get("/available", response_model=Dict[str, Dict[str, Any]])
async def get_available_strategies(
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Get all available strategy types and their information.

    Returns:
        Dictionary mapping strategy names to their metadata
    """
    try:
        strategies = strategy_service.get_available_strategies()
        return strategies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available strategies: {str(e)}",
        )


@router.get("/", response_model=DataResponse[List[StrategyResponse]])
async def get_user_strategies(
    include_public: bool = Query(True, description="Include public strategies"),
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Get all strategies for the current user.

    Args:
        include_public: Whether to include public strategies
        current_user: Current authenticated user

    Returns:
        List of user strategies
    """
    try:
        strategies = await strategy_service.get_user_strategies(
            current_user.id, include_public
        )

        return DataResponse(
            success=True,
            message=f"Retrieved {len(strategies)} strategies",
            data=strategies,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategies: {str(e)}",
        )


@router.post("/", response_model=DataResponse[StrategyResponse])
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Create a new trading strategy.

    Args:
        strategy_data: Strategy creation data
        current_user: Current authenticated user

    Returns:
        Created strategy
    """
    try:
        strategy = await strategy_service.create_strategy(
            current_user.id, strategy_data
        )

        # Convert SQLAlchemy model to Pydantic model and wrap in data response
        strategy_response = StrategyResponse.from_orm(strategy)
        return DataResponse(
            success=True,
            message="Strategy created successfully",
            data=strategy_response,
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create strategy: {str(e)}",
        )


@router.get("/{strategy_id}", response_model=DataResponse[StrategyResponse])
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Get a specific strategy by ID.

    Args:
        strategy_id: Strategy identifier
        current_user: Current authenticated user

    Returns:
        Strategy details
    """
    try:
        strategies = await strategy_service.get_user_strategies(current_user.id)
        strategy = next((s for s in strategies if s.id == strategy_id), None)

        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_id} not found",
            )

        return DataResponse(
            success=True, message="Strategy retrieved successfully", data=strategy
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy: {str(e)}",
        )


@router.put("/{strategy_id}", response_model=DataResponse[StrategyResponse])
async def update_strategy(
    strategy_id: str,
    strategy_data: StrategyUpdate,
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Update an existing strategy.

    Args:
        strategy_id: Strategy identifier
        strategy_data: Strategy update data
        current_user: Current authenticated user

    Returns:
        Updated strategy
    """
    try:
        strategy = await strategy_service.update_strategy(
            current_user.id, strategy_id, strategy_data
        )

        return DataResponse(
            success=True, message="Strategy updated successfully", data=strategy
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValidationError, BusinessLogicError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update strategy: {str(e)}",
        )


@router.delete("/{strategy_id}", response_model=BaseResponse)
async def delete_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Delete a strategy.

    Args:
        strategy_id: Strategy identifier
        current_user: Current authenticated user

    Returns:
        Success response
    """
    try:
        # Check if strategy has active deployments
        deployments = await strategy_service.get_user_deployments(
            current_user.id, active_only=True
        )
        active_deployments = [d for d in deployments if d.strategy_id == strategy_id]

        if active_deployments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete strategy with active deployments",
            )

        # For now, just mark as inactive (soft delete)
        # In a real implementation, you'd add a delete method to the service
        await strategy_service.update_strategy(
            current_user.id, strategy_id, StrategyUpdate(is_active=False)
        )

        return BaseResponse(success=True, message="Strategy deleted successfully")
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete strategy: {str(e)}",
        )


@router.post(
    "/{strategy_id}/deploy", response_model=DataResponse[StrategyDeploymentResponse]
)
async def deploy_strategy(
    strategy_id: str,
    deployment_data: StrategyDeploymentCreate,
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Deploy a strategy for live trading.

    Args:
        strategy_id: Strategy identifier
        deployment_data: Deployment configuration
        current_user: Current authenticated user

    Returns:
        Created deployment
    """
    try:
        # Ensure strategy_id matches the one in the URL
        deployment_data.strategy_id = strategy_id

        deployment = await strategy_service.deploy_strategy(
            current_user.id, deployment_data
        )

        return DataResponse(
            success=True, message="Strategy deployed successfully", data=deployment
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ValidationError, BusinessLogicError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy strategy: {str(e)}",
        )


@router.get(
    "/deployments/", response_model=DataResponse[List[StrategyDeploymentResponse]]
)
async def get_user_deployments(
    active_only: bool = Query(False, description="Return only active deployments"),
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Get all deployments for the current user.

    Args:
        active_only: Whether to return only active deployments
        current_user: Current authenticated user

    Returns:
        List of user deployments
    """
    try:
        deployments = await strategy_service.get_user_deployments(
            current_user.id, active_only
        )

        return DataResponse(
            success=True,
            message=f"Retrieved {len(deployments)} deployments",
            data=deployments,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployments: {str(e)}",
        )


@router.post(
    "/deployments/{deployment_id}/stop",
    response_model=DataResponse[StrategyDeploymentResponse],
)
async def stop_deployment(
    deployment_id: str,
    reason: Optional[str] = Query(None, description="Reason for stopping"),
    current_user: User = Depends(get_current_user),
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Stop a strategy deployment.

    Args:
        deployment_id: Deployment identifier
        reason: Optional reason for stopping
        current_user: Current authenticated user

    Returns:
        Updated deployment
    """
    try:
        deployment = strategy_service.stop_deployment(
            current_user.id, deployment_id, reason
        )

        return DataResponse(
            success=True, message="Deployment stopped successfully", data=deployment
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop deployment: {str(e)}",
        )


@router.post("/validate", response_model=BaseResponse)
async def validate_strategy_parameters(
    strategy_type: str,
    parameters: Dict[str, Any],
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    """
    Validate strategy parameters.

    Args:
        strategy_type: Strategy type name
        parameters: Parameters to validate

    Returns:
        Validation result
    """
    try:
        is_valid, error_message = await strategy_service.validate_strategy_parameters(
            strategy_type, parameters
        )

        if is_valid:
            return BaseResponse(success=True, message="Parameters are valid")
        else:
            return BaseResponse(
                success=False, message=f"Parameter validation failed: {error_message}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate parameters: {str(e)}",
        )
