list1 = [1, 2, 3, 4, 5]
list2 = [4, 5, 6, 7, 8]

element = 3

if element not in list1 and element not in list2:
    # Execute the code if the element is not present in both lists
    print("Element is not present in either list.")
else:
    # Execute alternative code if the element is present in at least one list
    print("Element is present in at least one list.")