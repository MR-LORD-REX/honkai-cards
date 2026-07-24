from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssetInfo(BaseModel):
    name: str
    icon: str


class CharacterSummary(BaseModel):
    id: str
    name: str
    eidolon: int
    level: int
    rarity: int
    element: AssetInfo
    path: AssetInfo
    icon: str
    splashArt: str
    portrait: str


class LightCone(BaseModel):
    id: str
    name: str
    rarity: int
    icon: str
    art: str
    superimpose: int


class Benchmark(BaseModel):
    percent: float | None = None
    rank: str | None = None


class BenchmarkDisplay(BaseModel):
    value: float | None = None
    type: str | None = None
    name: str | None = None


class Teammate(BaseModel):
    characterId: str
    icon: str
    eidolon: int
    lightConeId: str | None = None
    lightConeIcon: str | None = None
    superimposition: int


class ScoreStats(BaseModel):
    originalSimScore: float | None = None
    benchmarkSimScore: float | None = None
    perfectionSimScore: float | None = None
    benchmarkBaselineScore: float | None = None


class StatValue(BaseModel):
    name: str
    icon: str
    value: float
    isPercent: bool
    isDelta:bool=False


class SubstatValue(StatValue):
    rolledTimes: int | None = None


class StatBundle(BaseModel):
    model_config = ConfigDict(extra="allow")

    hp: StatValue | None = None
    atk: StatValue | None = None
    def_: StatValue | None = Field(default=None, alias="def")
    spd: StatValue | None = None
    critRate: StatValue | None = None
    critDmg: StatValue | None = None
    hpPercent: StatValue | None = None
    atkPercent: StatValue | None = None
    defPercent: StatValue | None = None
    ehr: StatValue | None = None
    res: StatValue | None = None
    be: StatValue | None = None
    err: StatValue | None = None
    ohb: StatValue | None = None
    elation: StatValue | None=None
    dmgBoost: StatValue | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class RelicScore(BaseModel):
    value: float
    rank: str


class Action(BaseModel):
    actionType:str
    actionName: str
    damage : float
    buffStat: str | None = None
        


class Relic(BaseModel):
    part: str
    set: str
    icon: str
    charIcon: str
    lvl: int
    isMaxed: bool
    grade: int
    mainStat: StatValue
    substats: list[SubstatValue]
    score: RelicScore


class BuildCardResponse(BaseModel):
    uid: int
    hasBenchmark: bool
    configType: str | None = None
    character: CharacterSummary
    lightCone: LightCone | None = None
    benchmark: Benchmark
    teammates: list[Teammate] | None = None
    scores: ScoreStats
    baseStats: StatBundle 
    combatStats: StatBundle | None = None
    benchmarkStats:StatBundle | None =None
    relics: list[Relic]
    actions: list[Action] = []
    benchmarkDisplay: BenchmarkDisplay | None = None