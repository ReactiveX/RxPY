def default_comparer(x, y):
	if not y.equals:
		return x == y
	
	return x.equals(y)

def create_message(actual, expected):
	return 'Expected: [' + str(expected + ']\r\nActual: [' + str(actual) + ']'

def are_elements_equal(expected, actual, comparer, message):
	is_ok = True
	comparer = comparer or defaultComparer
	if expected.length != actual.length:
		assert False, 'Not equal length. Expected: ' + expected.length + ' Actual: ' + actual.length
		return
	
	for ex in expected:
		isOk = comparer(ex, actual[i])
		if not is_ok:
			break
		
	assert is_ok, message or create_message(expected, actual)

def assert_equal(expected, actual) {
    return are_elements_equal(expected, actual, default_comparer)
