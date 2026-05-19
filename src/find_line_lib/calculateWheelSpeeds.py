def calculateWheelSpeeds(line: np.ndarray, base_speed: float = 50.0, max_gain_ratio: float = 0.8) -> tuple[float, float]:
    if line.shape[0] < 2:
        return base_speed, base_speed
        
    # 为了防止竖直方向的线导致斜率爆炸，统一用 y 拟合 x
    x = line[:, 0]
    y = line[:, 1]
    
    # 检查 y 的方差，防止分母为 0
    if np.var(y) < 1e-5:
        slope = 0.0
    else:
        # 拟合出 x = slope * y + intercept
        # 此时 slope 反映的是线偏向左还是偏向右，非常稳定！
        slope, _ = np.polyfit(y, x, 1)
    
    max_gain = base_speed * max_gain_ratio
    sensitivity = 2.0 
    
    # 限制 slope 的范围，防止 tanh 内部溢出锁死
    slope = np.clip(slope, -5.0, 5.0)
    
    calculate_gain = lambda s: max_gain * np.tanh(sensitivity * s)
    
    gain = calculate_gain(slope)
    
    # 转换逻辑：如果斜率向右偏，增加左轮速度，减小右轮速度以向左修正
    leftSpeed = base_speed + gain
    rightSpeed = base_speed - gain
    return float(leftSpeed), float(rightSpeed)

