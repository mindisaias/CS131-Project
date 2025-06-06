import numpy as np
from mock_classifier import clf, classify_scene  # Replace your_module_name with the filename (without .py)

# Test cases: each is (motion, light, hour) and expected label
# More extensive test cases: (motion, light, hour) and expected label
test_cases = [
    ((0, 0, 1), "unoccupied dark"),
    ((0, 3, 4), "unoccupied dark"),
    ((0, 5, 23), "unoccupied dark"),
    
    ((1, 2, 0), "occupied dark (night)"),
    ((1, 1, 22), "occupied dark (night)"),
    ((1, 3, 2), "occupied dark (night)"),
    
    ((1, 5, 10), "occupied dark (day)"),
    ((1, 4, 8), "occupied dark (day)"),
    ((1, 2, 18), "occupied dark (day)"),
    
    ((0, 6, 12), "unoccupied dim"),
    ((0, 20, 7), "unoccupied dim"),
    ((0, 25, 15), "unoccupied dim"),
    
    ((1, 15, 10), "occupied dim (day)"),
    ((1, 20, 14), "occupied dim (day)"),
    ((1, 24, 17), "occupied dim (day)"),
    
    ((1, 10, 23), "occupied dim (night)"),
    ((1, 12, 1), "occupied dim (night)"),
    ((1, 18, 4), "occupied dim (night)"),
    
    ((0, 30, 12), "unoccupied lit"),
    ((0, 50, 9), "unoccupied lit"),
    ((0, 100, 16), "unoccupied lit"),
    
    ((1, 45, 13), "occupied lit (day)"),
    ((1, 70, 11), "occupied lit (day)"),
    ((1, 90, 17), "occupied lit (day)"),
    
    ((1, 35, 21), "occupied lit (night)"),
    ((1, 60, 0), "occupied lit (night)"),
    ((1, 80, 3), "occupied lit (night)"),
    
    # Additional test cases (close to boundaries or new points)
    ((0, 4, 5), "unoccupied dark"),
    ((1, 25, 13), "occupied dim (day)"),
    ((1, 33, 22), "occupied lit (night)"),
    ((0, 55, 11), "unoccupied lit"),
    ((1, 65, 16), "occupied lit (day)"),
]

correct = 0
total = len(test_cases)

for i, (inputs, expected) in enumerate(test_cases, 1):
    motion, light, hour = inputs
    prediction = classify_scene(motion, light, hour)
    print(f"Test case {i}: Input={inputs}")
    print(f"Expected: {expected}")
    print(f"Predicted: {prediction}")
    if prediction == expected:
        print("Pass\n")
        correct += 1
    else:
        print("Fail\n")

accuracy = correct / total * 100
print(f"Prediction accuracy: {accuracy:.2f}% ({correct}/{total} correct)")
