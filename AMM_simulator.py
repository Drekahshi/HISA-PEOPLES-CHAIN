import math
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass, field
from decimal import Decimal, getcontext

# Set precision for financial calculations
getcontext().prec = 28

# Define all token symbols from your ecosystem
TOKEN_SYMBOLS = [
    "HISA", "USDC",
    "JANI", "CHAT", "UMOJA",
    "UMOJA_OPTION", "JANI_STABLE", "UMOJA_STABLE",
    "HBAR"
]

@dataclass
class Pool:
    """Represents a liquidity pool for two tokens in the AMM."""
    token_a_reserve: Decimal
    token_b_reserve: Decimal
    token_a_symbol: str
    token_b_symbol: str
    fee_rate: Decimal = Decimal('0.003')  # 0.3% fee

    @property
    def k(self) -> Decimal:
        """Constant product k = x * y for the pool."""
        return self.token_a_reserve * self.token_b_reserve

    @property
    def price_a_in_b(self) -> Decimal:
        """Price of token A in terms of token B."""
        if self.token_a_reserve == 0:
            return Decimal('0')
        return self.token_b_reserve / self.token_a_reserve

    @property
    def price_b_in_a(self) -> Decimal:
        """Price of token B in terms of token A."""
        if self.token_b_reserve == 0:
            return Decimal('0')
        return self.token_a_reserve / self.token_b_reserve

@dataclass
class EcosystemPool:
    """Represents a conceptual pool within a HISA ecosystem."""
    name: str
    purpose: str
    participants: List[str]
    rewards: List[str]
    mechanisms: List[str]

@dataclass
class Ecosystem:
    """Represents a HISA sub-ecosystem (JANI, UMOJA, CHAT)."""
    name: str
    description: str
    pools: List[EcosystemPool] = field(default_factory=list)

    def display(self):
        """Prints a formatted overview of the ecosystem and its pools."""
        print(f"\n=== {self.name} ===")
        print(f"{self.description}\n")
        for i, pool in enumerate(self.pools, 1):
            print(f"  {i}. {pool.name}")
            print(f"     Purpose: {pool.purpose}")
            print(f"     Participants: {', '.join(pool.participants)}")
            print(f"     Rewards: {', '.join(pool.rewards)}")
            print(f"     Mechanisms: {', '.join(pool.mechanisms)}\n")

class HISAAMM:
    """HISA Automated Market Maker implementation with ecosystem support."""

    def __init__(self):
        self.pools: Dict[str, Pool] = {}
        self.total_fees_collected = Decimal('0')
        self.ecosystems: Dict[str, Ecosystem] = self._initialize_hisa_ecosystems()
        self.initialize_amm_pools()

    def _initialize_hisa_ecosystems(self) -> Dict[str, Ecosystem]:
        """Initializes the conceptual HISA ecosystems (JANI, UMOJA, CHAT)."""
        jani = Ecosystem(
            name="🌿 JANI HISA (Conservation Ecosystem)",
            description="Focuses on tree planting, environmental regeneration, and carbon offset tokenization.",
            pools=[
                EcosystemPool(
                    name="Tree-Planting Staking Pool",
                    purpose="Reward verified planting and growth of trees.",
                    participants=["Farmers", "Nurseries", "Community Forest Associations"],
                    rewards=["JANI tokens", "NFTs", "Impact score badges"],
                    mechanisms=["Stake JANI", "Proof-of-Growth validation", "ZK oracles"]
                ),
                EcosystemPool(
                    name="Bamboo Carbon Offset Pool",
                    purpose="Incentivize bamboo farming for carbon credits.",
                    participants=["Bamboo Farmers", "Offset buyers"],
                    rewards=["HBAR tokens", "NFTs"],
                    mechanisms=["Staking", "Validator & AI verification", "Tokenized offsets"]
                ),
                EcosystemPool(
                    name="Validator Reward Pool",
                    purpose="Pay validators for verifying impact activities.",
                    participants=["Community validators", "AI agents"],
                    rewards=["JANI tokens", "Tiered validator bonuses"],
                    mechanisms=["GPS triangulation", "AI audit", "Staking + trust scores"]
                )
            ]
        )

        umoja = Ecosystem(
            name="🏛️ UMOJA HISA (Financial Ecosystem)",
            description="Focuses on tokenized prosperity, access to capital, and fractional finance.",
            pools=[
                EcosystemPool(
                    name="Fractional Ownership Pool",
                    purpose="Enable co-ownership of land, businesses, etc.",
                    participants=["Retail investors", "Local SMEs", "Farm cooperatives"],
                    rewards=["Yield", "Tokenized dividends"],
                    mechanisms=["Stake UMOJA", "Fractional asset tokens", "Governance"]
                ),
                EcosystemPool(
                    name="Microfinance & Chama Pool",
                    purpose="Empower communities to lend/borrow transparently.",
                    participants=["Chamas", "Women groups", "Youth SACCOs"],
                    rewards=["Interest", "Governance boosts"],
                    mechanisms=["DAO votes", "Loan tracking", "Staking UMOJA"]
                ),
                EcosystemPool(
                    name="Diaspora Investment Pool",
                    purpose="Let diaspora invest in African development projects.",
                    participants=["Diaspora funders", "Local entrepreneurs"],
                    rewards=["Yields", "Land shares", "Impact tokens"],
                    mechanisms=["Stake or donate", "Geo-targeted reporting", "Transparency dashboard"]
                )
            ]
        )

        chat = Ecosystem(
            name="🎤 CHAT HISA (Cultural Ecosystem)",
            description="Preserves, tokenizes, and rewards cultural memory through NFTs and voice-driven content.",
            pools=[
                EcosystemPool(
                    name="Voice-to-NFT Pool",
                    purpose="Monetize oral histories via AI transcription + tokenization.",
                    participants=["Elders", "Youth contributors"],
                    rewards=["CHAT tokens", "Royalties", "NFT minting rights"],
                    mechanisms=["Voice onboarding", "AI dialect tagging", "Mobile-to-IPFS"]
                ),
                EcosystemPool(
                    name="Curation DAO Pool",
                    purpose="Community votes to feature top cultural works.",
                    participants=["Token holders", "Curators", "Communities"],
                    rewards=["Revenue share", "Exposure in digital museums"],
                    mechanisms=["Quadratic voting", "Governance staking", "NFT feature rights"]
                ),
                EcosystemPool(
                    name="Licensing & Royalty Pool",
                    purpose="Distribute royalties from AR/VR and platform access.",
                    participants=["Creators", "Conservation vaults"],
                    rewards=["CHAT tokens", "Burn incentives"],
                    mechanisms=["Automated fee sharing", "NFT usage tracking", "Royalty splits"]
                )
            ]
        )
        return {"JANI": jani, "UMOJA": umoja, "CHAT": chat}

    def initialize_amm_pools(self):
        """Create initial liquidity pools for the HISA ecosystem AMM."""
        self.create_pool("HISA", "USDC", 100000, 500000)
        self.create_pool("JANI", "USDC", 50000, 250000)
        self.create_pool("CHAT", "USDC", 75000, 375000)
        self.create_pool("UMOJA", "USDC", 80000, 400000)
        self.create_pool("JANI_STABLE", "USDC", 200000, 200000, fee_rate=0.001)
        self.create_pool("UMOJA_STABLE", "USDC", 200000, 200000, fee_rate=0.001)
        self.create_pool("UMOJA_OPTION", "UMOJA", 1000000, 50000)
        self.create_pool("JANI", "JANI_STABLE", 50000, 50000)
        self.create_pool("UMOJA", "UMOJA_STABLE", 80000, 80000)
        self.create_pool("HBAR", "USDC", 200000, 100000)

    def create_pool(self, token_a: str, token_b: str,
                   initial_a: float, initial_b: float,
                   fee_rate: float = 0.003) -> str:
        if token_a not in TOKEN_SYMBOLS or token_b not in TOKEN_SYMBOLS:
            raise ValueError(f"Invalid token symbols. Valid tokens: {', '.join(TOKEN_SYMBOLS)}")
        pool_id = "-".join(sorted([token_a, token_b]))
        if pool_id in self.pools:
            raise ValueError(f"Pool {pool_id} already exists")
        self.pools[pool_id] = Pool(
            token_a_reserve=Decimal(str(initial_a)),
            token_b_reserve=Decimal(str(initial_b)),
            token_a_symbol=token_a,
            token_b_symbol=token_b,
            fee_rate=Decimal(str(fee_rate))
        )
        print(f"Created pool {pool_id}")
        print(f"Initial reserves: {initial_a} {token_a}, {initial_b} {token_b}")
        if token_a == self.pools[pool_id].token_a_symbol:
            print(f"Initial price: 1 {token_a} = {self.pools[pool_id].price_a_in_b:.6f} {token_b}")
        else:
            print(f"Initial price: 1 {token_a} = {self.pools[pool_id].price_b_in_a:.6f} {token_b}")
        return pool_id

    def get_swap_amount_out(self, pool_id: str, token_in: str,
                           amount_in: float) -> Tuple[Decimal, Decimal]:
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} does not exist")
        pool = self.pools[pool_id]
        amount_in_decimal = Decimal(str(amount_in))
        if token_in == pool.token_a_symbol:
            reserve_in = pool.token_a_reserve
            reserve_out = pool.token_b_reserve
        elif token_in == pool.token_b_symbol:
            reserve_in = pool.token_b_reserve
            reserve_out = pool.token_a_reserve
        else:
            raise ValueError(f"Token {token_in} not found in pool {pool_id}")
        fee_amount = amount_in_decimal * pool.fee_rate
        amount_in_after_fee = amount_in_decimal - fee_amount
        amount_out = (reserve_out * amount_in_after_fee) / (reserve_in + amount_in_after_fee)
        if amount_out < 0:
            amount_out = Decimal('0')
        return amount_out, fee_amount

    def execute_swap(self, pool_id: str, token_in: str, amount_in: float) -> Dict:
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} does not exist")
        pool = self.pools[pool_id]
        amount_out, fee = self.get_swap_amount_out(pool_id, token_in, amount_in)
        amount_in_decimal = Decimal(str(amount_in))
        token_out = pool.token_b_symbol if token_in == pool.token_a_symbol else pool.token_a_symbol
        if token_in == pool.token_a_symbol and amount_out > pool.token_b_reserve:
            raise ValueError(f"Insufficient {pool.token_b_symbol} liquidity.")
        elif token_in == pool.token_b_symbol and amount_out > pool.token_a_reserve:
            raise ValueError(f"Insufficient {pool.token_a_symbol} liquidity.")
        if token_in == pool.token_a_symbol:
            pool.token_a_reserve += amount_in_decimal
            pool.token_b_reserve -= amount_out
        else:
            pool.token_b_reserve += amount_in_decimal
            pool.token_a_reserve -= amount_out
        self.total_fees_collected += fee
        return {
            'pool_id': pool_id,
            'token_in': token_in,
            'amount_in': float(amount_in_decimal),
            'token_out': token_out,
            'amount_out': float(amount_out),
            'fee_paid': float(fee),
            'new_price_a_in_b': float(pool.price_a_in_b),
            'new_price_b_in_a': float(pool.price_b_in_a)
        }

    def add_liquidity(self, pool_id: str, amount_a: float, amount_b: float) -> Dict:
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} does not exist")
        if amount_a <= 0 or amount_b <= 0:
            raise ValueError("Amounts must be positive.")
        pool = self.pools[pool_id]
        amount_a_decimal = Decimal(str(amount_a))
        amount_b_decimal = Decimal(str(amount_b))
        if pool.token_a_reserve > 0 and pool.token_b_reserve > 0:
            current_ratio = pool.token_a_reserve / pool.token_b_reserve
            provided_ratio = amount_a_decimal / amount_b_decimal
            if abs(float(current_ratio - provided_ratio)) / float(current_ratio) > 0.001:
                print(f"Warning: Liquidity amounts don't match current pool ratio.")
                print(f"Current ratio (A/B): {float(current_ratio):.6f}")
                print(f"Provided ratio (A/B): {float(provided_ratio):.6f}")
        pool.token_a_reserve += amount_a_decimal
        pool.token_b_reserve += amount_b_decimal
        return {
            'pool_id': pool_id,
            'added_a': amount_a,
            'added_b': amount_b,
            'new_reserve_a': float(pool.token_a_reserve),
            'new_reserve_b': float(pool.token_b_reserve),
            'new_k': float(pool.k)
        }

    def get_pool_info(self, pool_id: str) -> Dict:
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} does not exist")
        pool = self.pools[pool_id]
        return {
            'pool_id': pool_id,
            'token_a': pool.token_a_symbol,
            'token_b': pool.token_b_symbol,
            'reserve_a': float(pool.token_a_reserve),
            'reserve_b': float(pool.token_b_reserve),
            'price_a_in_b': float(pool.price_a_in_b),
            'price_b_in_a': float(pool.price_b_in_a),
            'k': float(pool.k),
            'fee_rate': float(pool.fee_rate)
        }

    def simulate_price_impact(self, pool_id: str, token_in: str, amount_in: float) -> Dict:
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} does not exist")
        original_info = self.get_pool_info(pool_id)
        amount_out, fee = self.get_swap_amount_out(pool_id, token_in, amount_in)
        pool = self.pools[pool_id]
        hypothetical_token_a_reserve = pool.token_a_reserve
        hypothetical_token_b_reserve = pool.token_b_reserve
        if token_in == pool.token_a_symbol:
            hypothetical_token_a_reserve += Decimal(str(amount_in))
            hypothetical_token_b_reserve -= amount_out
        elif token_in == pool.token_b_symbol:
            hypothetical_token_b_reserve += Decimal(str(amount_in))
            hypothetical_token_a_reserve -= amount_out
        else:
            raise ValueError(f"Token {token_in} not in pool {pool_id}")
        new_price_a_in_b = hypothetical_token_b_reserve / hypothetical_token_a_reserve if hypothetical_token_a_reserve > 0 else Decimal('0')
        new_price_b_in_a = hypothetical_token_a_reserve / hypothetical_token_b_reserve if hypothetical_token_b_reserve > 0 else Decimal('0')
        if token_in == original_info['token_a']:
            price_impact = (new_price_a_in_b - Decimal(str(original_info['price_a_in_b']))) / Decimal(str(original_info['price_a_in_b']))
        else:
            price_impact = (new_price_b_in_a - Decimal(str(original_info['price_b_in_a']))) / Decimal(str(original_info['price_b_in_a']))
        return {
            'amount_out': float(amount_out),
            'fee': float(fee),
            'price_impact_percent': float(price_impact * 100),
            'new_price_a_in_b': float(new_price_a_in_b),
            'new_price_b_in_a': float(new_price_b_in_a)
        }

    def get_ecosystem_token_prices(self) -> Dict[str, float]:
        prices = {"USDC": 1.0}
        for pool_id, pool in self.pools.items():
            if pool.token_b_symbol == "USDC":
                prices[pool.token_a_symbol] = float(pool.price_a_in_b)
            elif pool.token_a_symbol == "USDC":
                prices[pool.token_b_symbol] = float(pool.price_b_in_a)
        found_new = True
        while found_new:
            found_new = False
            for pool_id, pool in self.pools.items():
                if pool.token_a_symbol not in prices and pool.token_b_symbol in prices:
                    prices[pool.token_a_symbol] = float(pool.price_a_in_b) * prices[pool.token_b_symbol]
                    found_new = True
                elif pool.token_b_symbol not in prices and pool.token_a_symbol in prices:
                    prices[pool.token_b_symbol] = float(pool.price_b_in_a) * prices[pool.token_a_symbol]
                    found_new = True
        return prices

class RewardCalculator:
    ARBITRAGE_THRESHOLD_PERCENT = 0.5

    def __init__(self, amm: HISAAMM):
        self.amm = amm

    def calculate_lp_rewards(self, pool_id: str, user_liquidity_percent: float,
                           time_period_days: int = 30) -> Dict:
        if pool_id not in self.amm.pools:
            raise ValueError(f"Pool {pool_id} does not exist")
        if not (0 <= user_liquidity_percent <= 100):
            raise ValueError("Liquidity percentage must be 0-100.")
        pool_info = self.amm.get_pool_info(pool_id)
        token_prices = self.amm.get_ecosystem_token_prices()
        token_a_price = token_prices.get(pool_info['token_a'], 0)
        token_b_price = token_prices.get(pool_info['token_b'], 0)
        token_a_value = pool_info['reserve_a'] * token_a_price
        token_b_value = pool_info['reserve_b'] * token_b_price
        total_liquidity_value = token_a_value + token_b_value
        if total_liquidity_value == 0:
            return {
                'user_liquidity_value': 0.0,
                'estimated_daily_volume': 0.0,
                'daily_fees_generated': 0.0,
                'user_daily_fee_share': 0.0,
                'user_period_rewards': 0.0,
                'estimated_apy': 0.0,
                'roi_percent': 0.0,
                'time_period_days': time_period_days
            }
        daily_volume = total_liquidity_value * 0.05
        daily_fees = daily_volume * float(self.amm.pools[pool_id].fee_rate)
        period_fees = daily_fees * time_period_days
        user_fee_share = period_fees * (user_liquidity_percent / 100)
        user_liquidity_value = total_liquidity_value * (user_liquidity_percent / 100)
        annual_fees = daily_fees * 365 * (user_liquidity_percent / 100)
        apy = (annual_fees / user_liquidity_value) * 100 * 30  if user_liquidity_value > 0 else 0
        roi = (user_fee_share / user_liquidity_value) * 100 if user_liquidity_value > 0 else 0
        return {
            'user_liquidity_value': user_liquidity_value,
            'estimated_daily_volume': daily_volume,
            'daily_fees_generated': daily_fees,
            'user_daily_fee_share': daily_fees * (user_liquidity_percent / 100),
            'user_period_rewards': user_fee_share,
            'estimated_apy': apy,
            'roi_percent': roi,
            'time_period_days': time_period_days
        }

    def calculate_arbitrage_opportunity(self, pool_id: str, external_price: float,
                                      token_symbol: str) -> Dict:
        pool_info = self.amm.get_pool_info(pool_id)
        if token_symbol not in TOKEN_SYMBOLS:
            raise ValueError(f"Invalid token symbol: {token_symbol}. Valid tokens: {', '.join(TOKEN_SYMBOLS)}")
        pool_price = 0.0
        if token_symbol == pool_info['token_a']:
            pool_price = pool_info['price_a_in_b']
            other_token_symbol = pool_info['token_b']
        elif token_symbol == pool_info['token_b']:
            pool_price = pool_info['price_b_in_a']
            other_token_symbol = pool_info['token_a']
        else:
            raise ValueError(f"Token {token_symbol} not in pool {pool_id}")
        if pool_price == 0:
            return {
                'pool_price': pool_price,
                'external_price': external_price,
                'price_difference': 0.0,
                'price_difference_percent': 0.0,
                'arbitrage_opportunity': False,
                'optimal_arbitrage_amount': 0.0,
                'estimated_profit': 0.0
            }
        price_difference = external_price - pool_price
        price_difference_percent = (price_difference / pool_price) * 100
        optimal_amount = 0.0
        potential_profit = 0.0
        if abs(price_difference_percent) > self.ARBITRAGE_THRESHOLD_PERCENT:
            pool = self.amm.pools[pool_id]
            reserve_in_decimal = pool.token_a_reserve if token_symbol == pool.token_a_symbol else pool.token_b_reserve
            optimal_amount = float(reserve_in_decimal) * 0.01
            potential_profit = abs(price_difference) * optimal_amount
        return {
            'pool_price': pool_price,
            'external_price': external_price,
            'price_difference': price_difference,
            'price_difference_percent': price_difference_percent,
            'arbitrage_opportunity': abs(price_difference_percent) > self.ARBITRAGE_THRESHOLD_PERCENT,
            'optimal_arbitrage_amount': optimal_amount,
            'estimated_profit': potential_profit
        }

def interactive_calculator():
    print("🌍 HISA Ecosystem AMM Interactive Calculator 🌿")
    print("="*60)
    amm = HISAAMM()
    calculator = RewardCalculator(amm)
    available_pools = list(amm.pools.keys())
    print("\nCurrent Ecosystem Token Prices (in USDC, estimated):")
    token_prices = amm.get_ecosystem_token_prices()
    for token, price in token_prices.items():
        print(f"  - {token}: {price:.6f}")
    while True:
        print("\n" + "="*60)
        print("Choose an option:")
        print("1. 💱 Swap Calculator")
        print("2. 💰 Liquidity Provider Rewards Calculator")
        print("3. 📊 Pool Information")
        print("4. 🔄 Arbitrage Opportunity Calculator")
        print("5. 🌐 Ecosystem Overview (JANI, UMOJA, CHAT)")
        print("6. 📋 Simplified Ecosystem Overview")
        print("7. 🚪 Exit")
        try:
            choice = input("\nEnter your choice (1-7): ").strip()
            if choice == "1":
                swap_calculator(amm, available_pools)
            elif choice == "2":
                lp_rewards_calculator(calculator, available_pools)
            elif choice == "3":
                display_pool_info(amm, available_pools)
            elif choice == "4":
                arbitrage_calculator(calculator, available_pools)
            elif choice == "5":
                ecosystem_overview(amm)
            elif choice == "6":
                simplified_ecosystem_overview()
            elif choice == "7":
                print("Thank you for using HISA Ecosystem Calculator! 👋")
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
        except KeyboardInterrupt:
            print("\n\nExiting... 👋")
            break
        except ValueError as ve:
            print(f"❌ Input Error: {ve}")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

def swap_calculator(amm: HISAAMM, available_pools: List[str]):
    print("\n💱 SWAP CALCULATOR")
    print("-" * 40)
    pool_id = select_pool(available_pools)
    if not pool_id:
        return
    pool_info = amm.get_pool_info(pool_id)
    print(f"\nPool: {pool_id}")
    print(f"Current price: 1 {pool_info['token_a']} = {pool_info['price_a_in_b']:.6f} {pool_info['token_b']}")
    try:
        token_in = input(f"\nWhich token do you want to swap? ({pool_info['token_a']}/{pool_info['token_b']}): ").strip().upper()
        if token_in not in [pool_info['token_a'], pool_info['token_b']]:
            print("❌ Invalid token selection.")
            return
        amount_in = float(input(f"How much {token_in} do you want to swap? "))
        if amount_in <= 0:
            print("❌ Amount must be positive.")
            return
        simulation = amm.simulate_price_impact(pool_id, token_in, amount_in)
        token_out = pool_info['token_b'] if token_in == pool_info['token_a'] else pool_info['token_a']
        print(f"\n📊 SWAP SIMULATION RESULTS:")
        print(f"Input: {amount_in:,.2f} {token_in}")
        print(f"Output: {simulation['amount_out']:,.6f} {token_out}")
        print(f"Trading Fee: {simulation['fee']:,.6f} {token_in}")
        print(f"Price Impact: {simulation['price_impact_percent']:,.4f}%")
        if amount_in > 0:
            print(f"Effective Exchange Rate: 1 {token_in} = {simulation['amount_out']/amount_in:.6f} {token_out}")
        execute = input("\n🚀 Execute this swap? (y/n): ").strip().lower()
        if execute == 'y':
            result = amm.execute_swap(pool_id, token_in, amount_in)
            print(f"✅ Swap executed successfully!")
            print(f"You received {result['amount_out']:,.6f} {result['token_out']}")
            print(f"New pool price (1 {pool_info['token_a']} = {result['new_price_a_in_b']:.6f} {pool_info['token_b']})")
        else:
            print("Swap not executed.")
    except ValueError as ve:
        print(f"❌ Invalid input: {ve}. Please enter numeric values.")
    except Exception as e:
        print(f"❌ Error during swap calculation: {e}")

def lp_rewards_calculator(calculator: RewardCalculator, available_pools: List[str]):
    print("\n💰 LIQUIDITY PROVIDER REWARDS CALCULATOR")
    print("-" * 50)
    pool_id = select_pool(available_pools)
    if not pool_id:
        return
    pool_info = calculator.amm.get_pool_info(pool_id)
    token_prices = calculator.amm.get_ecosystem_token_prices()
    token_a_price = token_prices.get(pool_info['token_a'], 0)
    token_b_price = token_prices.get(pool_info['token_b'], 0)
    token_a_value = pool_info['reserve_a'] * token_a_price
    token_b_value = pool_info['reserve_b'] * token_b_price
    total_pool_value = token_a_value + token_b_value
    if total_pool_value == 0:
        print(f"Pool {pool_id} has no liquidity. Cannot calculate rewards.")
        return
    print(f"\nPool: {pool_id}")
    print(f"Total Value Locked (TVL): ${total_pool_value:,.2f}")
    try:
        liquidity_amount = float(input("How much USD value would you like to provide as liquidity? $"))
        time_period = int(input("For how many days? "))
        if liquidity_amount <= 0 or time_period <= 0:
            print("❌ Values must be positive.")
            return
        liquidity_percentage = (liquidity_amount / total_pool_value) * 100
        rewards = calculator.calculate_lp_rewards(pool_id, liquidity_percentage, time_period)
        print(f"\n📊 LIQUIDITY PROVIDER REWARDS:")
        print(f"Your Liquidity: ${liquidity_amount:,.2f}")
        print(f"Your Pool Share: {rewards['user_liquidity_value']/total_pool_value*100:.4f}%")
        print(f"Estimated Daily Volume: ${rewards['estimated_daily_volume']:,.2f}")
        print(f"Your Daily Rewards: ${rewards['user_daily_fee_share']:,.6f}")
        print(f"Total Rewards ({time_period} days): ${rewards['user_period_rewards']:,.6f}")
        print(f"Estimated APY: {rewards['estimated_apy']:,.2f}%")
        print(f"ROI ({time_period} days): {rewards['roi_percent']:,.2f}%")
        token_a_needed = (liquidity_amount / 2) / token_a_price if token_a_price > 0 else 0
        token_b_needed = (liquidity_amount / 2) / token_b_price if token_b_price > 0 else 0
        print(f"\n🪙 TOKENS NEEDED FOR LIQUIDITY (50/50 split):")
        if token_a_needed > 0:
            print(f"{pool_info['token_a']} required: {token_a_needed:,.2f} (${liquidity_amount/2:,.2f})")
        else:
            print(f"{pool_info['token_a']} required: Price unavailable.")
        if token_b_needed > 0:
            print(f"{pool_info['token_b']} required: {token_b_needed:,.2f} (${liquidity_amount/2:,.2f})")
        else:
            print(f"{pool_info['token_b']} required: Price unavailable.")
    except ValueError as ve:
        print(f"❌ Invalid input: {ve}. Please enter numeric values.")
    except Exception as e:
        print(f"❌ Error during LP rewards calculation: {e}")

def arbitrage_calculator(calculator: RewardCalculator, available_pools: List[str]):
    print("\n🔄 ARBITRAGE OPPORTUNITY CALCULATOR")
    print("-" * 40)
    pool_id = select_pool(available_pools)
    if not pool_id:
        return
    pool_info = calculator.amm.get_pool_info(pool_id)
    token_symbol = input(f"Which token are you checking for arbitrage? ({pool_info['token_a']}/{pool_info['token_b']}): ").strip().upper()
    if token_symbol not in [pool_info['token_a'], pool_info['token_b']]:
        print("❌ Invalid token selection.")
        return
    try:
        other_token_symbol = pool_info['token_b'] if token_symbol == pool_info['token_a'] else pool_info['token_a']
        if token_symbol == pool_info['token_a']:
            print(f"Current pool price: 1 {token_symbol} = {pool_info['price_a_in_b']:.6f} {other_token_symbol}")
            external_price = float(input(f"What's the external market price for 1 {token_symbol} in {other_token_symbol}? "))
        else:
            print(f"Current pool price: 1 {token_symbol} = {pool_info['price_b_in_a']:.6f} {other_token_symbol}")
            external_price = float(input(f"What's the external market price for 1 {token_symbol} in {other_token_symbol}? "))
        arbitrage = calculator.calculate_arbitrage_opportunity(pool_id, external_price, token_symbol)
        print(f"\n📊 ARBITRAGE ANALYSIS:")
        print(f"Pool Price: {arbitrage['pool_price']:,.6f}")
        print(f"External Price: {arbitrage['external_price']:,.6f}")
        print(f"Price Difference: {arbitrage['price_difference']:,.6f} ({arbitrage['price_difference_percent']:+.2f}%)")
        if arbitrage['arbitrage_opportunity']:
            print(f"✅ Arbitrage Opportunity Detected! (Price difference > {calculator.ARBITRAGE_THRESHOLD_PERCENT}%)")
            print(f"Estimated Optimal Trade Size: {arbitrage['optimal_arbitrage_amount']:,.2f} {token_symbol}")
            print(f"Estimated Profit: ${arbitrage['estimated_profit']:,.6f}")
        else:
            print(f"❌ No significant arbitrage opportunity")
    except ValueError as ve:
        print(f"❌ Invalid input: {ve}. Please enter numeric values.")
    except Exception as e:
        print(f"❌ Error during arbitrage calculation: {e}")

def display_pool_info(amm: HISAAMM, available_pools: List[str]):
    print("\n📊 POOL INFORMATION")
    print("-" * 30)
    pool_id = select_pool(available_pools)
    if not pool_id:
        return
    info = amm.get_pool_info(pool_id)
    token_prices = amm.get_ecosystem_token_prices()
    token_a_price = token_prices.get(info['token_a'], 0)
    token_b_price = token_prices.get(info['token_b'], 0)
    token_a_value = info['reserve_a'] * token_a_price
    token_b_value = info['reserve_b'] * token_b_price
    total_pool_value = token_a_value + token_b_value
    print(f"\nPool: {pool_id}")
    print(f"{info['token_a']} Reserve: {info['reserve_a']:,.2f} " + (f"(${token_a_value:,.2f})" if token_a_price > 0 else "(Price N/A)"))
    print(f"{info['token_b']} Reserve: {info['reserve_b']:,.2f} " + (f"(${token_b_value:,.2f})" if token_b_price > 0 else "(Price N/A)"))
    print(f"Total Value Locked (TVL): ${total_pool_value:,.2f}")
    print(f"Current Price: 1 {info['token_a']} = {info['price_a_in_b']:.6f} {info['token_b']}")
    print(f"Constant K: {info['k']:,.2f}")
    print(f"Trading Fee: {info['fee_rate']*100:.1f}%")

def ecosystem_overview(amm: HISAAMM):
    print("\n🌐 HISA ECOSYSTEM OVERVIEW")
    print("-" * 40)
    for eco_name, eco_obj in amm.ecosystems.items():
        eco_obj.display()
    print("\n--- AMM Liquidity Pools Summary ---")
    token_prices = amm.get_ecosystem_token_prices()
    print("\nEstimated Token Prices (in USDC):")
    for token, price in token_prices.items():
        print(f"  - {token}: {price:.6f}")
    print("\nLiquidity Pools:")
    total_tvl_across_amm = 0
    for pool_id, pool in amm.pools.items():
        token_a_price = token_prices.get(pool.token_a_symbol, 0)
        token_b_price = token_prices.get(pool.token_b_symbol, 0)
        pool_tvl = 0
        if token_a_price > 0 and token_b_price > 0:
            token_a_value = float(pool.token_a_reserve) * token_a_price
            token_b_value = float(pool.token_b_reserve) * token_b_price
            pool_tvl = token_a_value + token_b_value
            total_tvl_across_amm += pool_tvl
        print(f"  - {pool_id}:")
        print(f"      Reserves: {float(pool.token_a_reserve):,.2f} {pool.token_a_symbol} + {float(pool.token_b_reserve):,.2f} {pool.token_b_symbol}")
        print(f"      TVL: ${pool_tvl:,.2f}" if pool_tvl > 0 else "      TVL: Price data unavailable")
        print(f"      Price: 1 {pool.token_a_symbol} = {pool.price_a_in_b:.6f} {pool.token_b_symbol}")
    print(f"\nTotal Value Locked (TVL) across all AMM pools: ${total_tvl_across_amm:,.2f}")
    print(f"Total Fees Collected by AMM: ${float(amm.total_fees_collected):,.2f}")

def simplified_ecosystem_overview():
    from dataclasses import dataclass, field
    from typing import List

    @dataclass
    class SimplePool:
        name: str
        purpose: str
        participants: List[str]
        rewards: List[str]
        mechanisms: List[str]

    @dataclass
    class SimpleEcosystem:
        name: str
        description: str
        pools: List[SimplePool] = field(default_factory=list)

        def display(self):
            print(f"\n=== {self.name} ===")
            print(f"{self.description}\n")
            for i, pool in enumerate(self.pools, 1):
                print(f"  {i}. {pool.name}")
                print(f"     Purpose: {pool.purpose}")
                print(f"     Participants: {', '.join(pool.participants)}")
                print(f"     Rewards: {', '.join(pool.rewards)}")
                print(f"     Mechanisms: {', '.join(pool.mechanisms)}\n")

    print("\n📋 SIMPLIFIED HISA ECOSYSTEM OVERVIEW")
    print("-" * 40)

    jani = SimpleEcosystem(
        name="🌿 JANI HISA (Conservation Ecosystem)",
        description="Focuses on tree planting, environmental regeneration, and carbon offset tokenization.",
        pools=[
            SimplePool(
                name="Tree-Planting Staking Pool",
                purpose="Reward verified planting and growth of trees.",
                participants=["Farmers", "Nurseries", "Community Forest Associations"],
                rewards=["JANI tokens", "NFTs", "Impact score badges"],
                mechanisms=["Stake JANI", "Proof-of-Growth validation", "ZK oracles"]
            ),
            SimplePool(
                name="Bamboo Carbon Offset Pool",
                purpose="Incentivize bamboo farming for carbon credits.",
                participants=["Bamboo Farmers", "Offset buyers"],
                rewards=["HBAR tokens", "NFTs"],
                mechanisms=["Staking", "Validator & AI verification", "Tokenized offsets"]
            ),
            SimplePool(
                name="Validator Reward Pool",
                purpose="Pay validators for verifying impact activities.",
                participants=["Community validators", "AI agents"],
                rewards=["JANI tokens", "Tiered validator bonuses"],
                mechanisms=["GPS triangulation", "AI audit", "Staking + trust scores"]
            )
        ]
    )

    umoja = SimpleEcosystem(
        name="🏛️ UMOJA HISA (Financial Ecosystem)",
        description="Focuses on tokenized prosperity, access to capital, and fractional finance.",
        pools=[
            SimplePool(
                name="Fractional Ownership Pool",
                purpose="Enable co-ownership of land, businesses, etc.",
                participants=["Retail investors", "Local SMEs", "Farm cooperatives"],
                rewards=["Yield", "Tokenized dividends"],
                mechanisms=["Stake UMOJA", "Fractional asset tokens", "Governance"]
            ),
            SimplePool(
                name="Microfinance & Chama Pool",
                purpose="Empower communities to lend/borrow transparently.",
                participants=["Chamas", "Women groups", "Youth SACCOs"],
                rewards=["Interest", "Governance boosts"],
                mechanisms=["DAO votes", "Loan tracking", "Staking UMOJA"]
            ),
            SimplePool(
                name="Diaspora Investment Pool",
                purpose="Let diaspora invest in African development projects.",
                participants=["Diaspora funders", "Local entrepreneurs"],
                rewards=["Yields", "Land shares", "Impact tokens"],
                mechanisms=["Stake or donate", "Geo-targeted reporting", "Transparency dashboard"]
            )
        ]
    )

    chat = SimpleEcosystem(
        name="🎤 CHAT HISA (Cultural Ecosystem)",
        description="Preserves, tokenizes, and rewards cultural memory through NFTs and voice-driven content.",
        pools=[
            SimplePool(
                name="Voice-to-NFT Pool",
                purpose="Monetize oral histories via AI transcription + tokenization.",
                participants=["Elders", "Youth contributors"],
                rewards=["CHAT tokens", "Royalties", "NFT minting rights"],
                mechanisms=["Voice onboarding", "AI dialect tagging", "Mobile-to-IPFS"]
            ),
            SimplePool(
                name="Curation DAO Pool",
                purpose="Community votes to feature top cultural works.",
                participants=["Token holders", "Curators", "Communities"],
                rewards=["Revenue share", "Exposure in digital museums"],
                mechanisms=["Quadratic voting", "Governance staking", "NFT feature rights"]
            ),
            SimplePool(
                name="Licensing & Royalty Pool",
                purpose="Distribute royalties from AR/VR and platform access.",
                participants=["Creators", "Conservation vaults"],
                rewards=["CHAT tokens", "Burn incentives"],
                mechanisms=["Automated fee sharing", "NFT usage tracking", "Royalty splits"]
            )
        ]
    )

    for eco in [jani, umoja, chat]:
        eco.display()

def select_pool(available_pools: List[str]) -> Optional[str]:
    if not available_pools:
        return None
    print("\nAvailable Pools:")
    for i, pool_id in enumerate(available_pools, 1):
        print(f"{i}. {pool_id}")
    try:
        choice_str = input("\nSelect a pool by number (or 'b' to go back): ").strip().lower()
        if choice_str == 'b':
            return None
        choice = int(choice_str)
        if 1 <= choice <= len(available_pools):
            return available_pools[choice-1]
        else:
            print("❌ Invalid selection.")
            return None
    except ValueError:
        print("❌ Invalid input.")
        return None

if __name__ == "__main__":
    interactive_calculator()
