#!/usr/bin/env python3
"""
Unified exchange client for derivatives data.

Provides consistent interface across multiple exchanges with:
- Rate limiting and retry logic
- Data normalization
- Mock data for simulation
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
import random
import time


class Exchange(Enum):
    """Supported exchanges."""

    BINANCE = "binance"
    BYBIT = "bybit"
    OKX = "okx"
    DERIBIT = "deribit"
    BITMEX = "bitmex"


@dataclass
class FundingRate:
    """Funding rate data point."""

    exchange: str
    symbol: str
    rate: Decimal  # Current 8-hour rate
    predicted_rate: Decimal  # Next predicted rate
    next_payment: datetime  # Time of next payment
    interval_hours: int = 8  # Funding interval

    @property
    def annualized(self) -> float:
        """Calculate annualized funding rate."""
        return float(self.rate) * (365 * 24 / self.interval_hours) * 100

    @property
    def time_to_payment(self) -> timedelta:
        """Time until next funding payment."""
        return self.next_payment - datetime.now()

    @property
    def time_to_payment_str(self) -> str:
        """Human-readable time to payment."""
        delta = self.time_to_payment
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"


@dataclass
class OpenInterest:
    """Open interest data point."""

    exchange: str
    symbol: str
    oi_usd: Decimal  # Total OI in USD
    oi_contracts: Decimal  # Total contracts
    change_1h_pct: float  # 1h change
    change_24h_pct: float  # 24h change
    change_7d_pct: float  # 7d change
    long_ratio: float  # Long/short ratio (1.0 = balanced)
    timestamp: datetime


@dataclass
class Liquidation:
    """Single liquidation event."""

    exchange: str
    symbol: str
    side: str  # "long" or "short"
    price: Decimal
    quantity: Decimal
    value_usd: Decimal
    timestamp: datetime


@dataclass
class LiquidationLevel:
    """Aggregated liquidation level."""

    price: Decimal
    side: str  # "long" or "short"
    total_value_usd: Decimal
    density: str  # "low", "medium", "high", "critical"


@dataclass
class OptionsSnapshot:
    """Options market snapshot."""

    symbol: str
    exchange: str
    expiry: str
    atm_iv: float  # At-the-money IV
    put_call_ratio_volume: float  # Put/call by volume
    put_call_ratio_oi: float  # Put/call by OI
    max_pain: Decimal  # Max pain price
    total_call_oi: Decimal
    total_put_oi: Decimal
    timestamp: datetime


@dataclass
class BasisData:
    """Futures basis for one exchange and one dated expiry (a term-structure point)."""

    exchange: str
    symbol: str
    expiry: str  # ISO date of the dated future
    days_to_expiry: int
    spot_price: Decimal
    futures_price: Decimal
    basis_pct: float  # (futures - spot) / spot, in percent
    annualized_pct: float  # basis_pct scaled to a 365-day year


class ExchangeClient:
    """
    Unified client for fetching derivatives data from exchanges.

    Uses mock data for demonstration. In production, replace with
    actual API calls.
    """

    # Rate limits by exchange
    RATE_LIMITS = {
        Exchange.BINANCE: {"rpm": 1200, "delay": 0.05},
        Exchange.BYBIT: {"rpm": 120, "delay": 0.5},
        Exchange.OKX: {"rpm": 60, "delay": 1.0},
        Exchange.DERIBIT: {"rpm": 100, "delay": 0.6},
        Exchange.BITMEX: {"rpm": 30, "delay": 2.0},
    }

    def __init__(self, use_mock: bool = True):
        """
        Initialize exchange client.

        Args:
            use_mock: Use mock data (True) or live APIs (False)
        """
        self.use_mock = use_mock
        self._last_request: Dict[Exchange, float] = {}

    def _rate_limit(self, exchange: Exchange):
        """Apply rate limiting for exchange."""
        delay = self.RATE_LIMITS[exchange]["delay"]
        last = self._last_request.get(exchange, 0)
        elapsed = time.time() - last
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self._last_request[exchange] = time.time()

    # -------------------------------------------------------------------------
    # Funding Rate Methods
    # -------------------------------------------------------------------------

    def get_funding_rate(
        self,
        symbol: str,
        exchange: Exchange,
    ) -> Optional[FundingRate]:
        """Get funding rate for symbol on exchange."""
        if self.use_mock:
            return self._mock_funding_rate(symbol, exchange)

        self._rate_limit(exchange)
        # Production: implement actual API calls
        raise NotImplementedError("Live API not implemented")

    def get_all_funding_rates(
        self,
        symbol: str,
        exchanges: Optional[List[Exchange]] = None,
    ) -> List[FundingRate]:
        """Get funding rates from all exchanges."""
        if exchanges is None:
            exchanges = list(Exchange)

        rates = []
        for exchange in exchanges:
            rate = self.get_funding_rate(symbol, exchange)
            if rate:
                rates.append(rate)

        return rates

    def _mock_funding_rate(
        self,
        symbol: str,
        exchange: Exchange,
    ) -> FundingRate:
        """Generate mock funding rate."""
        # Base rates vary by exchange
        base_rates = {
            Exchange.BINANCE: 0.0150,
            Exchange.BYBIT: 0.0180,
            Exchange.OKX: 0.0130,
            Exchange.DERIBIT: 0.0200,
            Exchange.BITMEX: 0.0100,
        }

        base = base_rates.get(exchange, 0.0100)
        # Add some randomness
        rate = base + random.uniform(-0.005, 0.005)
        predicted = rate + random.uniform(-0.002, 0.002)

        # Next funding payment (8-hour intervals)
        now = datetime.now()
        # Find next 00:00, 08:00, or 16:00 UTC
        hours_since_midnight = now.hour
        next_funding_hour = ((hours_since_midnight // 8) + 1) * 8
        if next_funding_hour >= 24:
            next_payment = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        else:
            next_payment = now.replace(hour=next_funding_hour, minute=0, second=0)
            if next_payment <= now:
                next_payment += timedelta(hours=8)

        return FundingRate(
            exchange=exchange.value,
            symbol=symbol,
            rate=Decimal(str(round(rate, 6))),
            predicted_rate=Decimal(str(round(predicted, 6))),
            next_payment=next_payment,
        )

    # -------------------------------------------------------------------------
    # Open Interest Methods
    # -------------------------------------------------------------------------

    def get_open_interest(
        self,
        symbol: str,
        exchange: Exchange,
    ) -> Optional[OpenInterest]:
        """Get open interest for symbol on exchange."""
        if self.use_mock:
            return self._mock_open_interest(symbol, exchange)

        self._rate_limit(exchange)
        raise NotImplementedError("Live API not implemented")

    def get_all_open_interest(
        self,
        symbol: str,
        exchanges: Optional[List[Exchange]] = None,
    ) -> List[OpenInterest]:
        """Get open interest from all exchanges."""
        if exchanges is None:
            exchanges = list(Exchange)

        oi_list = []
        for exchange in exchanges:
            oi = self.get_open_interest(symbol, exchange)
            if oi:
                oi_list.append(oi)

        return oi_list

    def _mock_open_interest(
        self,
        symbol: str,
        exchange: Exchange,
    ) -> OpenInterest:
        """Generate mock open interest data."""
        # Base OI varies by exchange (in billions USD)
        base_oi = {
            Exchange.BINANCE: 8.2,
            Exchange.BYBIT: 4.5,
            Exchange.OKX: 3.1,
            Exchange.DERIBIT: 1.2,
            Exchange.BITMEX: 1.5,
        }

        oi_usd = base_oi.get(exchange, 1.0) * 1_000_000_000
        # Add randomness
        oi_usd *= 1 + random.uniform(-0.1, 0.1)

        # Calculate contracts (assuming ~$67k BTC)
        if symbol == "BTC":
            price = 67500
        elif symbol == "ETH":
            price = 2500
            oi_usd *= 0.4  # ETH has ~40% of BTC OI
        else:
            price = 100
            oi_usd *= 0.1

        contracts = oi_usd / price

        return OpenInterest(
            exchange=exchange.value,
            symbol=symbol,
            oi_usd=Decimal(str(int(oi_usd))),
            oi_contracts=Decimal(str(int(contracts))),
            change_1h_pct=round(random.uniform(-2, 3), 2),
            change_24h_pct=round(random.uniform(-5, 8), 2),
            change_7d_pct=round(random.uniform(-10, 15), 2),
            long_ratio=round(1.0 + random.uniform(-0.2, 0.3), 2),
            timestamp=datetime.now(),
        )

    # -------------------------------------------------------------------------
    # Liquidation Methods
    # -------------------------------------------------------------------------

    def get_recent_liquidations(
        self,
        symbol: str,
        exchange: Optional[Exchange] = None,
        limit: int = 50,
        min_value_usd: float = 100000,
    ) -> List[Liquidation]:
        """Get recent liquidation events."""
        if self.use_mock:
            return self._mock_liquidations(symbol, limit, min_value_usd)

        raise NotImplementedError("Live API not implemented")

    def get_liquidation_levels(
        self,
        symbol: str,
        current_price: Decimal,
    ) -> List[LiquidationLevel]:
        """Get aggregated liquidation levels."""
        if self.use_mock:
            return self._mock_liquidation_levels(symbol, current_price)

        raise NotImplementedError("Live API not implemented")

    def _mock_liquidations(
        self,
        symbol: str,
        limit: int,
        min_value_usd: float,
    ) -> List[Liquidation]:
        """Generate mock liquidation events."""
        liquidations = []
        exchanges = [e.value for e in Exchange]

        if symbol == "BTC":
            base_price = 67500
        elif symbol == "ETH":
            base_price = 2500
        else:
            base_price = 100

        for i in range(limit):
            side = random.choice(["long", "short"])
            # Liquidation prices cluster around support/resistance
            if side == "long":
                price = base_price * (1 - random.uniform(0.01, 0.05))
            else:
                price = base_price * (1 + random.uniform(0.01, 0.05))

            value = random.uniform(min_value_usd, min_value_usd * 50)
            quantity = value / price

            liquidations.append(
                Liquidation(
                    exchange=random.choice(exchanges),
                    symbol=symbol,
                    side=side,
                    price=Decimal(str(round(price, 2))),
                    quantity=Decimal(str(round(quantity, 4))),
                    value_usd=Decimal(str(int(value))),
                    timestamp=datetime.now() - timedelta(minutes=random.randint(1, 1440)),
                )
            )

        return sorted(liquidations, key=lambda x: x.timestamp, reverse=True)

    def _mock_liquidation_levels(
        self,
        symbol: str,
        current_price: Decimal,
    ) -> List[LiquidationLevel]:
        """Generate mock liquidation level clusters."""
        levels = []
        price = float(current_price)

        # Long liquidation levels (below current price)
        long_levels = [
            (price * 0.96, 125_000_000, "high"),
            (price * 0.93, 85_000_000, "medium"),
            (price * 0.89, 210_000_000, "critical"),
            (price * 0.85, 150_000_000, "high"),
        ]

        # Short liquidation levels (above current price)
        short_levels = [
            (price * 1.04, 95_000_000, "medium"),
            (price * 1.07, 145_000_000, "high"),
            (price * 1.11, 180_000_000, "high"),
            (price * 1.15, 120_000_000, "medium"),
        ]

        for lvl_price, value, density in long_levels:
            levels.append(
                LiquidationLevel(
                    price=Decimal(str(int(lvl_price))),
                    side="long",
                    total_value_usd=Decimal(str(int(value * random.uniform(0.8, 1.2)))),
                    density=density,
                )
            )

        for lvl_price, value, density in short_levels:
            levels.append(
                LiquidationLevel(
                    price=Decimal(str(int(lvl_price))),
                    side="short",
                    total_value_usd=Decimal(str(int(value * random.uniform(0.8, 1.2)))),
                    density=density,
                )
            )

        return sorted(levels, key=lambda x: x.price)

    # -------------------------------------------------------------------------
    # Options Methods
    # -------------------------------------------------------------------------

    def get_options_snapshot(
        self,
        symbol: str,
        expiry: Optional[str] = None,
    ) -> Optional[OptionsSnapshot]:
        """Get options market snapshot."""
        if self.use_mock:
            return self._mock_options_snapshot(symbol, expiry)

        raise NotImplementedError("Live API not implemented")

    def _mock_options_snapshot(
        self,
        symbol: str,
        expiry: Optional[str] = None,
    ) -> OptionsSnapshot:
        """Generate mock options snapshot."""
        if symbol == "BTC":
            max_pain = 67000
            atm_iv = 55 + random.uniform(-5, 10)
        elif symbol == "ETH":
            max_pain = 2500
            atm_iv = 60 + random.uniform(-5, 15)
        else:
            max_pain = 100
            atm_iv = 80 + random.uniform(-10, 20)

        if expiry is None:
            # Default to next Friday
            expiry = "2025-01-17"

        call_oi = random.uniform(1, 5) * 1_000_000_000
        put_oi = call_oi * random.uniform(0.6, 0.9)

        return OptionsSnapshot(
            symbol=symbol,
            exchange="deribit",
            expiry=expiry,
            atm_iv=round(atm_iv, 1),
            put_call_ratio_volume=round(random.uniform(0.5, 1.2), 2),
            put_call_ratio_oi=round(put_oi / call_oi, 2),
            max_pain=Decimal(str(max_pain)),
            total_call_oi=Decimal(str(int(call_oi))),
            total_put_oi=Decimal(str(int(put_oi))),
            timestamp=datetime.now(),
        )

    # -------------------------------------------------------------------------
    # Basis Methods
    # -------------------------------------------------------------------------

    def get_all_basis(
        self,
        symbol: str,
        spot_price: Decimal,
        exchanges: Optional[List[Exchange]] = None,
    ) -> List[BasisData]:
        """Get the dated-futures term structure across exchanges.

        Returns one BasisData per exchange and quarterly expiry, measured
        against the supplied spot price.
        """
        if exchanges is None:
            exchanges = list(Exchange)

        if self.use_mock:
            points: List[BasisData] = []
            for exchange in exchanges:
                points.extend(self._mock_basis_curve(symbol, Decimal(spot_price), exchange))
            return points

        raise NotImplementedError("Live API not implemented")

    @staticmethod
    def _quarterly_expiries(today: datetime, count: int = 3) -> List[datetime]:
        """Last Friday of the next `count` quarter-end months (Mar/Jun/Sep/Dec)."""
        expiries: List[datetime] = []
        year, month = today.year, today.month
        while len(expiries) < count:
            if month in (3, 6, 9, 12):
                first_next = datetime(year + (month == 12), month % 12 + 1, 1)
                last_day = first_next - timedelta(days=1)
                last_friday = last_day - timedelta(days=(last_day.weekday() - 4) % 7)
                if last_friday.date() > today.date():
                    expiries.append(last_friday)
            month += 1
            if month > 12:
                month, year = 1, year + 1
        return expiries

    def _mock_basis_curve(
        self,
        symbol: str,
        spot_price: Decimal,
        exchange: Exchange,
    ) -> List[BasisData]:
        """Generate a mock contango curve: basis grows with time to expiry."""
        now = datetime.now()
        spot = float(spot_price)
        points: List[BasisData] = []
        for expiry in self._quarterly_expiries(now):
            days = max((expiry.date() - now.date()).days, 1)
            # Typical crypto carry: roughly 5-12% annualized, with exchange noise
            annual = random.uniform(5.0, 12.0)
            basis_pct = annual * days / 365
            futures = spot * (1 + basis_pct / 100)
            points.append(
                BasisData(
                    exchange=exchange.value,
                    symbol=symbol,
                    expiry=expiry.strftime("%Y-%m-%d"),
                    days_to_expiry=days,
                    spot_price=Decimal(str(round(spot, 2))),
                    futures_price=Decimal(str(round(futures, 2))),
                    basis_pct=round(basis_pct, 3),
                    annualized_pct=round(basis_pct * 365 / days, 2),
                )
            )
        return points


def demo():
    """Demonstrate exchange client."""
    client = ExchangeClient(use_mock=True)

    print("=" * 60)
    print("EXCHANGE CLIENT DEMO")
    print("=" * 60)

    # Funding rates
    print("\n📊 BTC Funding Rates:")
    rates = client.get_all_funding_rates("BTC")
    for rate in rates:
        print(f"  {rate.exchange:<10} {float(rate.rate):+.4%} | Annualized: {rate.annualized:+.2f}%")

    # Open interest
    print("\n📈 BTC Open Interest:")
    oi_list = client.get_all_open_interest("BTC")
    total = sum(float(oi.oi_usd) for oi in oi_list)
    for oi in sorted(oi_list, key=lambda x: x.oi_usd, reverse=True):
        share = float(oi.oi_usd) / total * 100
        print(
            f"  {oi.exchange:<10} ${float(oi.oi_usd) / 1e9:.1f}B | 24h: {oi.change_24h_pct:+.1f}% | Share: {share:.1f}%"
        )

    # Basis
    print("\n💱 BTC Basis:")
    for point in client.get_all_basis("BTC", Decimal("67500"), [Exchange.BINANCE]):
        print(
            f"  {point.exchange:<10} {point.expiry} ({point.days_to_expiry}d) "
            f"${point.futures_price:,.2f} basis {point.basis_pct:+.3f}% "
            f"annualized {point.annualized_pct:+.2f}%"
        )


if __name__ == "__main__":
    demo()
