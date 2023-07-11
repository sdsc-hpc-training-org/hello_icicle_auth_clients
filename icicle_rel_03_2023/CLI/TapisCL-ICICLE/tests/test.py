def engage_in_silliness(request1, request2, answer = {}):
    answer[request1] = request2
    return answer

z = engage_in_silliness('a', 'b')
y = engage_in_silliness('b', 'c')
print(y)