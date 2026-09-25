
# GG_Digital_SWE_2026
# Filename: GG_Digital_SWE_2026.py
 
 
 
from typing import List, Dict, Tuple
import itertools
import time
import random
import numpy as np
from scipy.optimize import linear_sum_assignment
 
class RidePricingOptimizer:
    def __init__(self):
        self.cost_per_ride = 3.0 #gives the value per cost
        #self.price_options = [5, 7, 8, 10, 12, 15]  Available price points, however doesn't really make sense
        self.price_options = [5, 10, 19, 20, 14]
        self.cost_per_mile = 0.5 #decided on this because there is oppurunity cost and also gas prices to account for
                
        
    def brute_optimizer(self, base_demands):
 
        """
        Try every combination of prices across all periods and keep the best.
        Guaranteed optimal. Cost: O(k^n) where k = len(price_options),
        n = number of periods. Fine for small periods which is true in this case
        however it is unfeisable in terms of many periods which would provide more accurate data.
        """
        n = len(base_demands) # storing the number of time periods in base demands 
        best_prices = None 
        best_profit = float("-inf") #start the profit below any possible profit so that first combination always wins
 
        for combo in itertools.product(self.price_options, repeat=n): #this is a python tool that takes every single combination repeated for n times
            profit = self.simulate_day(base_demands, list(combo)) #evaluate a single combinations profit accounting for deferred customers & store it
            if profit > best_profit: 
                best_profit = profit
                best_prices = list(combo)
 
        return best_prices #returns optimal prices for each period
 
    def dynamic_optimizer(self, base_demands):
        """
        Dynamic programming: exact like brute force, but better for time consideration.
        Key idea: the best profit from period t onward depends ONLY on
        (t, how many deferred customers arrive), not on earlier prices.
        So we cache each (t, deferred) answer instead of recomputing it.
        """
        n = len(base_demands)  # number of time periods
 
        n = len(base_demands)
        memo = {}  # (t, carried) -> (profit, plan)
 
        def best_from(t, carried):
            if (t, carried) in memo:      # already solved this state, reuse it
                return memo[(t, carried)]
 
            if t == n:                     # base case: no periods left
                memo[(t, carried)] = (0.0, ())
                return memo[(t, carried)]
 
            best_profit = float("-inf")
            best_plan = ()
 
 
            best_profit = float("-inf")  # any real profit beats this
            best_plan = ()               # prices for periods t..n-1
 
            for price in self.price_options:  # try every price for THIS period
                # Demand now = new requests + customers deferred from last period
                total_demand = base_demands[t] + carried
                served, deferred = self.calculate_demand_and_spillover(total_demand, price)
 
                # Profit earned this period
                profit_now = (price - self.cost_per_ride) * served
 
                # Best possible profit for all later periods, given who we defer.
                # This recursive call
                future_profit, future_plan = best_from(t + 1, deferred)
 
                total = profit_now + future_profit
                if total > best_profit:  # strict > keeps the first (lowest) price on ties
                    best_profit = total
                    best_plan = (price,) + future_plan  # this price + best later prices
 
            return best_profit, best_plan
 
        # Start at period 0 with nobody deferred; keep only the price plan
        _, plan = best_from(0, 0)
        return list(plan)
 
        
 
 
 
 
    
    def simulate_day(self, base_demands, prices):
        """
        Simulate one full day with the given prices and return total profit.
        Make sure to handle spillover effects and demand calculations.
        Use this to evaluate your pricing strategy.
 
        
        Args:
            base_demands: Base demand for each period
            prices: Price in each period
            
        Returns:
            Total profit for the day
        """
        if len(base_demands) != len(prices): 
            raise ValueError("base_demands and prices must have same length")
        
        total_profit = 0
        deferred_customers = 0  # Number of spillover customers
        
        for period in range(len(base_demands)):
            # Total demand = base demand + spillover
            total_demand = base_demands[period] + deferred_customers
            
            actual_customers, new_deferred = self.calculate_demand_and_spillover( #, lost
                total_demand, prices[period] #, dropout_rate
            )
            
            # Calculate profit for this period
            period_profit = (prices[period] - self.cost_per_ride) * actual_customers #subtract
            total_profit += period_profit

            #total_profit -= lost*(prices[period] - self.cost_per_ride)
            
            # Update spillover customers for next period
            deferred_customers = new_deferred
       
        return total_profit
    
 
 
    def calculate_demand_and_spillover(self, total_demand, price,): # droupout_rate=0.25
        """
        Calculate actual ridership and spillover based on price.
        - Low prices (<$10): Everyone rides, no deferrals
        - Medium prices ($10-$19): 10% of customers defer to next period  
        - High prices ($20+): 30% of customers defer to next period
        - Of anyone deferred, a fraction (dropout_rate) leaves permanently
        instead of coming back next period — this is what makes deferring
        a real cost instead of a free delay.
        
        Args:
            total_demand: Total customers wanting rides this period
            price: Price being charged
            
        Returns:
            (actual_customers_this_period, customers_deferred_to_next_period)
        """
        if price <= 10:
            return total_demand, 0
        elif price <= 20:
            deferred = int(total_demand * 0.1)
            actual = total_demand - deferred
            return actual, deferred
        else:  # price >= 21:
            deferred = int(total_demand * 0.3)
            actual = total_demand - deferred
            return actual, deferred

        """
        if price <= 10:
        deferred_raw = 0
    elif price <= 20:
        deferred_raw = int(total_demand * 0.1)
    else:
        deferred_raw = int(total_demand * 0.3)
    actual = total_demand - deferred_raw
    lost = int(deferred_raw * dropout_rate)
    carried_forward = deferred_raw - lost
    return actual, carried_forward, lost
    """
 
 
 
 
 
    def compare_algorithms(self, base_demands):
        results = {}
 
        # Brute force
        start = time.time()
        brute_prices = self.brute_optimizer(base_demands)
        brute_time = time.time() - start
        brute_profit = self.simulate_day(base_demands, brute_prices)
        results["Brute Force"] = {
            "prices": brute_prices,
            "profit": brute_profit,
            "time": brute_time,
        }
 
        # Dynamic programming
        start = time.time()
        dp_prices = self.dynamic_optimizer(base_demands)
        dp_time = time.time() - start
        dp_profit = self.simulate_day(base_demands, dp_prices)
        results["Dynamic Programming"] = {
            "prices": dp_prices,
            "profit": dp_profit,
            "time": dp_time,
        }
 
        return results
 

    def match_random(self, rider_locations, driver_locations, price, rng):
        """Pairs riders to drivers in arbitrary random order -- no optimization."""
        n = min(len(rider_locations), len(driver_locations))
        riders = list(range(len(rider_locations)))
        drivers = list(range(len(driver_locations)))
        rng.shuffle(riders)
        rng.shuffle(drivers)
 
        total_distance = 0.0
        for i in range(n):
            rx, ry = rider_locations[riders[i]]
            dx, dy = driver_locations[drivers[i]]
            total_distance += ((rx - dx) ** 2 + (ry - dy) ** 2) ** 0.5
 
        profit = (price - self.cost_per_ride) * n - self.cost_per_mile * total_distance
        return n, total_distance, profit
 
    def match_bipartite(self, rider_locations, driver_locations, price):
        """Pairs riders to drivers using Graph Theory Biparite matching -- minimum total distance."""
        n_riders, n_drivers = len(rider_locations), len(driver_locations)
        cost_matrix = np.array([
            [((rx - dx) ** 2 + (ry - dy) ** 2) ** 0.5 for dx, dy in driver_locations]
            for rx, ry in rider_locations
        ])
        row_ind, col_ind = linear_sum_assignment(cost_matrix)   # <- the optimal matching step
 
        n = len(row_ind)
        total_distance = cost_matrix[row_ind, col_ind].sum()
        profit = (price - self.cost_per_ride) * n - self.cost_per_mile * total_distance
        return n, total_distance, profit
 
  
    def compare_matching_strategies(self, base_demands, drivers_per_period, city_size= 10.0, seed= 42):
        """ same location to run each program random and not random """
        prices = self.dynamic_optimizer(base_demands)
        rng = random.Random(seed)
 
        rows = []
        deferred = 0
        for period in range(len(base_demands)):
            total_demand = base_demands[period] + deferred
            actual, price_deferred = self.calculate_demand_and_spillover(total_demand, prices[period])
 
            # same locations fed to both matching strategies -- only the pairing differs
            riders = [(rng.uniform(0, city_size), rng.uniform(0, city_size)) for _ in range(actual)]
            drivers = [(rng.uniform(0, city_size), rng.uniform(0, city_size)) for _ in range(drivers_per_period[period])]
 
            r_completed, r_distance, r_profit = self.match_random(riders, drivers, prices[period], rng)
            b_completed, b_distance, b_profit = self.match_bipartite(riders, drivers, prices[period])
 
            rows.append({
                "period": period, "price": prices[period],
                "completed": b_completed,  # same for both -- matching choice doesn't change WHO rides, only distance
                "random_distance": r_distance, "random_profit": r_profit,
                "bipartite_distance": b_distance, "bipartite_profit": b_profit,
                "gain": b_profit - r_profit,
            })
 
            deferred = price_deferred + max(0, actual - b_completed)
 
        return rows
 
 
    
if __name__ == "__main__":
    optimizer = RidePricingOptimizer()
    
    # Sample demand pattern: morning, lunch, evening, night
    base_demands = [20, 50, 80, 60, 40]  # Small example for testing, add 2 more demands to see difference
    
    print(f"Base demands: {base_demands}")
    print(f"Available prices: {optimizer.price_options}")
    print(f"Cost per ride: ${optimizer.cost_per_ride}\n")
    
    # Test simulation
    test_prices = [8, 10, 12, 8, 20] #add two more to see difference
    test_profit = optimizer.simulate_day(base_demands, test_prices)
    print(f"Test prices {test_prices} -> Profit: ${test_profit:.2f}\n")
    
    # Run your optimization
    results = optimizer.compare_algorithms(base_demands)
    
    for algorithm, result in results.items():
        print(f"{algorithm}:")
        print(f"  Prices: {result['prices']}")
        print(f"  Profit: ${result['profit']:.2f}")
        print(f"  Time: {result['time']:.2f}")
 
 
if __name__ == "__main__":
    optimizer = RidePricingOptimizer()
 
    base_demands = [30, 20, 50, 25]
    drivers_per_period = [22, 18, 35, 20]
 
    rows = optimizer.compare_matching_strategies(base_demands, drivers_per_period)
 
    print(f"{'Period':<7}{'Price':<7}{'Rides':<7}{'Random Dist':<13}{'Bipartite Dist':<16}{'Random $':<11}{'Bipartite $':<13}{'Gain':<8}")
    for r in rows:
        print(f"{r['period']:<7}${r['price']:<6}{r['completed']:<7}"
              f"{r['random_distance']:<13.1f}{r['bipartite_distance']:<16.1f}"
              f"${r['random_profit']:<10.2f}${r['bipartite_profit']:<12.2f}${r['gain']:<7.2f}")
 
    total_random = sum(r["random_profit"] for r in rows)
    total_bipartite = sum(r["bipartite_profit"] for r in rows)
    print(f"\nTotal profit -- random matching:    ${total_random:.2f}")
    print(f"Total profit -- bipartite matching:  ${total_bipartite:.2f}")
    print(f"Bipartite matching's gain:           ${total_bipartite - total_random:.2f}")
 
