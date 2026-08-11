import { useState } from "react";
import "./PremiumCalculator.css";

function PremiumCalculator() {
  const [startingBalance, setStartingBalance] = useState(10000);
  const [annualRate, setAnnualRate] = useState(8);
  const [duration, setDuration] = useState(10);
  const [periodicAddition, setPeriodicAddition] = useState(500);
  const [frequency, setFrequency] = useState("monthly");

  const [result, setResult] = useState({
    finalBalance: 0,
    totalContributions: 0,
    totalInterest: 0,
  });

  const calculateInterest = () => {
    const starting = parseFloat(startingBalance) || 0;
    const rate = parseFloat(annualRate) || 0;
    const years = parseFloat(duration) || 0;
    const addition = parseFloat(periodicAddition) || 0;

    let periodsPerYear;

    switch (frequency) {
      case "yearly":
        periodsPerYear = 1;
        break;

      case "quarterly":
        periodsPerYear = 4;
        break;

      case "monthly":
        periodsPerYear = 12;
        break;

      case "weekly":
        periodsPerYear = 52;
        break;

      default:
        periodsPerYear = 12;
    }

    const periodicRate = rate / 100 / periodsPerYear;

    const totalPeriods = Math.floor(years * periodsPerYear);

    let balance = starting;
    let totalContributions = 0;

    for (let i = 0; i < totalPeriods; i++) {
      balance = balance * (1 + periodicRate);

      balance += addition;

      totalContributions += addition;
    }

    const totalInterest = balance - starting - totalContributions;

    setResult({
      finalBalance: balance,
      totalContributions,
      totalInterest,
    });
  };

  const formatCurrency = (amount) => {
    return (
      new Intl.NumberFormat("en-NP", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(amount) + " NPR"
    );
  };

  return (
    <div className="calculator-wrapper">
      <div className="calculator">
        {/* INPUTS */}

        <div className="calculator-inputs">
          <h1>Premium Calculator</h1>

          <p className="calculator-description">
            Calculate your estimated investment growth, contributions and
            interest.
          </p>

          <div className="form-group">
            <label>Starting Balance</label>

            <input
              type="number"
              value={startingBalance}
              min="0"
              step="0.01"
              onChange={(e) => setStartingBalance(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Annual Return Rate (%)</label>

            <input
              type="number"
              value={annualRate}
              min="0"
              step="0.01"
              onChange={(e) => setAnnualRate(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Duration (Years)</label>

            <input
              type="number"
              value={duration}
              min="1"
              step="1"
              onChange={(e) => setDuration(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Periodic Addition</label>

            <input
              type="number"
              value={periodicAddition}
              min="0"
              step="0.01"
              onChange={(e) => setPeriodicAddition(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Compound / Addition Frequency</label>

            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
            >
              <option value="yearly">Yearly</option>

              <option value="quarterly">Quarterly</option>

              <option value="monthly">Monthly</option>

              <option value="weekly">Weekly</option>
            </select>
          </div>

          <button
            type="button"
            className="calculate-btn"
            onClick={calculateInterest}
          >
            Calculate
          </button>
        </div>

        {/* RESULT */}

        <div className="calculator-result">
          <h2>Calculation Result</h2>

          <div className="result-main">
            <div className="result-label">Final Balance</div>

            <div className="final-amount">
              {formatCurrency(result.finalBalance)}
            </div>
          </div>

          <div className="result-items">
            <div className="result-item">
              <span>Starting Balance</span>

              <span>{formatCurrency(parseFloat(startingBalance) || 0)}</span>
            </div>

            <div className="result-item">
              <span>Total Contributions</span>

              <span>{formatCurrency(result.totalContributions)}</span>
            </div>

            <div className="result-item">
              <span>Total Interest</span>

              <span>{formatCurrency(result.totalInterest)}</span>
            </div>

            <div className="result-item">
              <span>Annual Return</span>

              <span>{(parseFloat(annualRate) || 0).toFixed(2)}%</span>
            </div>

            <div className="result-item">
              <span>Duration</span>

              <span>{duration || 0} years</span>
            </div>

            <div className="result-item">
              <span>Frequency</span>

              <span>
                {frequency.charAt(0).toUpperCase() + frequency.slice(1)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PremiumCalculator;
