from fastapi.params import Query
from agent_platform_service.controllers.interface import api, interface_api
from agent_platform_service.fastapi_fields.req.interface_api.menu_click_request import MenuClickRequest
from agent_platform_service.fastapi_fields.resp.console.app_resp import AppStatistics, AppProvinceStatistics
from agent_platform_service.fastapi_fields.resp.interface_api.menu_click_response import MenuClickResponse
from fastapi import Depends
from agent_platform_service.services.statistics_service import StatisticsService


@interface_api.get("/statistics/app-count", response_model=AppStatistics)
async def app_statistics_api_get(statistics_service: StatisticsService = Depends(StatisticsService)):
    stat = await statistics_service.get_app_statistics()
    return AppStatistics(agent=stat["agent"], workflow=stat["workflow"])


@interface_api.get("/statistics/app-count-province", response_model=AppProvinceStatistics)
async def app_statistics_api_get(type: str=Query(...,
                                                description="The type of statistics to retrieve. Can be 'total' for all-time statistics or 'month' for monthly statistics."),
                                 statistics_service: StatisticsService = Depends(StatisticsService)):
    result = await statistics_service.get_app_by_province_statistics(type)
    return AppProvinceStatistics(data=result)

@interface_api.post("/statistics/menuClickLog/addInterface", response_model=MenuClickResponse)
async def app_statistics_menu_click(req: MenuClickRequest, statistics_service: StatisticsService = Depends(StatisticsService)):
    return await statistics_service.add_api(json=req.model_dump())