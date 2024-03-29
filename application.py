import constants as const
import utils
import collections
from enumeration import Enum
from tabulate import tabulate
from database import Query
from database import Mongo


def handle_search_plan():
    """
    OPTION - Search Insurance Plan

    """
    print("\n==============Insurance Plan==============")
    constrains = collections.OrderedDict()

    # 1. Decide plan objectives
    keys = list(Enum.mark_cov_type.keys())
    utils.print_series(keys, "Plan Coverage", showindex=True)
    instruction = "\nWhich plan coverage are you looking for?: "
    values = list(str(i) for i in range(len(keys)))
    plan_obj = wait_input(instruction, values)
    if plan_obj == -1:
        return
    constrains[const.MARK_COVERAGE] = (const.EQUAL, Enum.mark_cov_type[keys[int(plan_obj)]])

    # 2. Decide plan type (medical/dental)
    instruction = "\nWhich type of insurance do you want to query? (medical/dental): "
    values = ["medical", "dental"]
    insurance_type = wait_input(instruction, values)
    if insurance_type == -1:
        return

    # 3. Handle different plan type
    search_plan_sub_menu(constrains, insurance_type)


def search_plan_sub_menu(constrains, insurance_type):
    """
    Sub Menu - Search Plan Using Dynamic Filter(s).

    :param constrains: filter constrains
    :param insurance_type: medical/dental plan
    """
    plans = list()
    options = list()
    options.append((1, "Select Plans"))
    options.append((2, "Add Filter"))
    options.append((3, "Remove Filter"))
    options.append((4, "Back to Menu"))
    attributes = [const.PLAN_ID, const.PLAN_VAR_NAME]
    detailed_constrains = collections.OrderedDict()

    while True:
        # Query the plans from database
        plans = Query.get_plans(attributes=attributes,
                                constrains=constrains,
                                detail_constrains=detailed_constrains,
                                insurance_type=insurance_type)
        # Update the record number
        options[0] = (1, "Show plans ({})".format(len(plans)))

        print("\n==========Insurance Plan - {} - {}=========="
              .format(insurance_type.upper(), Enum.mark_cov_type_rev[constrains[const.MARK_COVERAGE][1]]))
        utils.print_data_frame(options, ["Index", "Option"])
        index = input("\nPlease select an option:")
        if index.strip() == "1":
            # Handle "Select Plans"
            instruction = "You can select a plan for detail information: "
            ind = display_in_pages(plans, attributes, instruction, showindex=True)
            if ind >= 0:
                plan_id = plans[ind][0]
                search_plan_detail_information(plan_id)

        elif index.strip() == "2":
            # Handle "Add Filter"
            if insurance_type == "medical":
                search_plan_add_filter_medical(constrains, detailed_constrains)
            else:
                search_plan_add_filter_dental(constrains, detailed_constrains)

        elif index.strip() == "3":
            # Handle "Remove Filter"
            search_plan_remove_filter(constrains, detailed_constrains, insurance_type)

        elif index.strip() == "4":
            # Handle "Quit"
            print("Bye.")
            return

        else:
            print("Invalid Index.")


def search_plan_detail_information(plan_id):
    """
    Sub Menu - Looking for detail information of selected plan

    :param plan_id: plan ID
    """
    options = list()
    options.append((1, "Disease Programs"))
    options.append((2, "Plan Benefits"))
    options.append((3, "Plan Detail"))
    options.append((4, "Quit"))
    while True:
        print("\n==========Plan Information==========")
        utils.print_data_frame(options, ["Index", "Option"])
        instruction = "\nPlease select an option:"
        values = list(str(i) for i in range(1, 1 + len(options)))
        index = wait_input(instruction, values)
        if index == -1:
            return

        if index == '1':
            # Display disease programs the plan offered
            disease_str = Mongo.get_disease_programs(const.COL_MEDICAL_DISEASE, plan_id)
            if disease_str is None:
                print("\nDisease Programs are not offered for this plan.")
            else:
                disease_list = disease_str.split(",")
                utils.print_series(disease_list, "Disease Program")

            input("\nPress any key to continue.")

        elif index == '2':
            # Display benefits the plan covered
            attr_db = [const.BENEFIT_NAME]
            attr_output = ["Benefit Name"]
            constrains = dict()
            constrains[const.PLAN_ID] = (const.EQUAL, plan_id)
            info = Query.plain_query(attr_db, const.TABLE_BENEFIT, constrains, order_by=const.BENEFIT_NAME)
            display_in_pages(info, attr_output)

        elif index == '3':
            # Display the general information of the plan
            attr_db = [const.PLAN_ID,
                       const.PLAN_VAR_NAME,
                       const.PLAN_STATE,
                       const.PLAN_TYPE,
                       const.QHP_TYPE,
                       const.IS_NEW_PLAN,
                       const.CHILD_ONLY,
                       const.EFFECTIVE_DATE,
                       const.EXPIRATION_DATE,
                       const.URL_BROCHURE]
            constrains = dict()
            constrains[const.PLAN_ID] = (const.EQUAL, plan_id)
            info = Query.plain_query_one(attr_db, const.TABLE_PLAN, constrains)
            plan_info = list()
            plan_info.append(("Plan ID", info[0]))
            plan_info.append(("Plan Name", info[1]))
            plan_info.append(("State", info[2]))
            plan_info.append(("Plan Type", Enum.plan_type_rev[info[3]]))
            plan_info.append(("QHP Type", Enum.qhp_type_rev[info[4]]))
            plan_info.append(("Is New Plan", ("No", "Yes")[info[5]]))
            plan_info.append(("Child Option", Enum.child_only_type_rev[info[6]]))
            plan_info.append(("Effective Date", info[7]))
            plan_info.append(("Expiration Date", info[8]))
            plan_info.append(("URL", info[9]))
            utils.print_single_data(plan_info)
            input("\nPress any key to continue.")

        elif index == '4' or index == 'quit':
            return
        else:
            print("Invalid Index.")


def search_plan_add_filter_medical(constrains, detail_constrains):
    """
    Add a filter for medical plan

    :param constrains: current constains on <plans> table
    :param detail_constrains: detail constrains on <medical_plans> table
    """
    filters = list()
    filters.append((1, "State"))
    filters.append((2, "Plan Type"))
    filters.append((3, "QHP Type"))
    filters.append((4, "Child Option"))
    filters.append((5, "Metal level"))
    filters.append((6, "Notice for pregnancy Required"))
    filters.append((7, "Wellness Program Offered"))
    filters.append((8, "Quit"))

    utils.print_data_frame(filters, ["Index", "Filter"])
    instruction = "\nPlease select an filter:"
    values = list(str(i) for i in range(1, 1 + len(filters)))
    index = wait_input(instruction, values)
    if index == -1:
        return
    if index.strip() == "1":
        # Decide constrains for state
        state_list = Query.get_plan_state()
        utils.print_data_frame(state_list, ["State"])
        instruction = "\nPlease select a state: "
        values = list(value[0] for value in state_list)
        state = wait_input(instruction, values)
        if state == -1:
            return
        constrains[const.PLAN_STATE] = (const.EQUAL, state)

    elif index.strip() == "2":
        # Decide constrains for plan type
        keys = list(Enum.plan_type.keys())
        utils.print_series(keys, "Plan Type", showindex=True)
        instruction = "\nWhich type of plan do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        constrains[const.PLAN_TYPE] = (const.EQUAL, Enum.plan_type[keys[int(index)]])

    elif index.strip() == "3":
        # Decide constrains for QHP type
        keys = list(Enum.qhp_type.keys())
        utils.print_series(keys, "QHP Type", showindex=True)
        instruction = "\nWhich QHP type do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        constrains[const.QHP_TYPE] = (const.EQUAL, Enum.qhp_type[keys[int(index)]])

    elif index.strip() == "4":
        # Decide constrains for child option
        keys = list(Enum.child_only_type.keys())
        utils.print_series(keys, "Child Option", showindex=True)
        instruction = "\nWhich child option do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        constrains[const.CHILD_ONLY] = (const.EQUAL, Enum.child_only_type[keys[int(index)]])

    elif index.strip() == "5":
        # Decide constrains for metal level
        keys = list(Enum.m_metal_type.keys())
        utils.print_series(keys, "Metal Level", showindex=True)
        instruction = "\nWhich metal level do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        detail_constrains[const.M_METAL_LEVEL] = (const.EQUAL, Enum.m_metal_type[keys[int(index)]])

    elif index.strip() == "6":
        # Decide constrains for pregnancy notice
        instruction = "\nWhether notice required for pregnancy?(yes/no): "
        values = ["yes", "no"]
        value = wait_input(instruction, values)
        if value == -1:
            return
        detail_constrains[const.PREG_NOTICE] = (const.EQUAL, True) if value == "yes" else (const.EQUAL, False)

    elif index.strip() == "7":
        # Decide constrains for wellness program of plan
        instruction = "\nDo you want wellness program included?(yes/no): "
        values = ["yes", "no"]
        value = wait_input(instruction, values)
        if value == -1:
            return
        detail_constrains[const.WELLNESS_OFFER] = (const.EQUAL, True) if value == "yes" else (const.EQUAL, False)

    elif index.strip() == "8":
        print("Quit.")
        return
    else:
        print("Invalid Index.")


def search_plan_add_filter_dental(constrains, detail_constrains):
    """
    Add a filter for medical plan for dental plan

    :param constrains: current constains on <plans> table
    :param detail_constrains: detail constrains on <dental_plans> table
    """
    filters = list()
    filters.append((1, "State"))
    filters.append((2, "Plan Type"))
    filters.append((3, "QHP Type"))
    filters.append((4, "Child Option"))
    filters.append((5, "Metal level"))
    filters.append((6, "Quit"))

    utils.print_data_frame(filters, ["Index", "Filter"])
    instruction = "\nPlease select an filter:"
    values = list(str(i) for i in range(1, 1 + len(filters)))
    index = wait_input(instruction, values)
    if index == -1:
        return

    if index.strip() == "1":
        # Decide constrains for state
        state_list = Query.get_plan_state()
        utils.print_data_frame(state_list, ["State"])
        instruction = "\nPlease select a state: "
        values = list(value[0] for value in state_list)
        state = wait_input(instruction, values)
        if state == -1:
            return
        constrains[const.PLAN_STATE] = (const.EQUAL, state)

    elif index.strip() == "2":
        # Decide constrains for plan type
        keys = list(Enum.plan_type.keys())
        utils.print_series(keys, "Plan Type", showindex=True)
        instruction = "\nWhich type of plan do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        constrains[const.PLAN_TYPE] = (const.EQUAL, Enum.plan_type[keys[int(index)]])

    elif index.strip() == "3":
        # Decide constrains for QHP type
        keys = list(Enum.qhp_type.keys())
        utils.print_series(keys, "QHP Type", showindex=True)
        instruction = "\nWhich QHP type do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        constrains[const.QHP_TYPE] = (const.EQUAL, Enum.qhp_type[keys[int(index)]])

    elif index.strip() == "4":
        # Decide constrains for child option
        keys = list(Enum.child_only_type.keys())
        utils.print_series(keys, "Child Option", showindex=True)
        instruction = "\nWhich child option do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        constrains[const.CHILD_ONLY] = (const.EQUAL, Enum.child_only_type[keys[int(index)]])

    elif index.strip() == "5":
        # Decide constrains for metal level
        keys = list(Enum.d_metal_type.keys())
        utils.print_series(keys, "Metal Level", showindex=True)
        instruction = "\nWhich metal level do you want?: "
        values = list(str(i) for i in range(len(keys)))
        index = wait_input(instruction, values)
        if index == -1:
            return
        detail_constrains[const.M_METAL_LEVEL] = (const.EQUAL, Enum.d_metal_type[keys[int(index)]])

    elif index.strip() == "6":
        print("Quit.")
        return
    else:
        print("Invalid Index.")


def search_plan_remove_filter(constrains, detail_constrains, insurance_type):
    """
    Remove the current filter(s) that is selected.

    :param constrains: current constains on <plans> table
    :param detail_constrains: detail constrains on <medical_plan>/<dental_plan> table
    :param insurance_type: medical/dental insurance
    """
    cur_filters = list()

    # Check current filter(s)
    if const.PLAN_TYPE in constrains:
        value = int(constrains[const.PLAN_TYPE][1])
        cur_filters.append(("Plan Type", Enum.plan_type_rev[value]))

    if const.QHP_TYPE in constrains:
        value = int(constrains[const.QHP_TYPE][1])
        cur_filters.append(("QHP Type", Enum.qhp_type_rev[value]))

    if const.CHILD_ONLY in constrains:
        value = int(constrains[const.CHILD_ONLY][1])
        cur_filters.append(("Child Option", Enum.child_only_type_rev[value]))

    if const.PLAN_STATE in constrains:
        value = constrains[const.PLAN_STATE][1]
        cur_filters.append(("State", value))

    if insurance_type == "medical":
        if const.M_METAL_LEVEL in detail_constrains:
            value = int(detail_constrains[const.M_METAL_LEVEL][1])
            cur_filters.append(("Metal Level", Enum.m_metal_type_rev[value]))

        if const.WELLNESS_OFFER in detail_constrains:
            value = detail_constrains[const.WELLNESS_OFFER][1]
            value_desc = "Yes" if value else "No"
            cur_filters.append(("Wellness Program", value_desc))

        if const.PREG_NOTICE in detail_constrains:
            value = detail_constrains[const.PREG_NOTICE][1]
            value_desc = "Yes" if value else "No"
            cur_filters.append(("Pregnancy Notice", value_desc))
    else:
        if const.D_METAL_LEVEL in detail_constrains:
            value = int(detail_constrains[const.D_METAL_LEVEL][1])
            cur_filters.append(("Metal Level", Enum.d_metal_type_rev[value]))

    # If do not have any filter, then return
    if not cur_filters:
        print("\nNo filter.")
        input("\nPress any key to continue.")
        return
    cur_filters.append(("Quit", "-"))
    utils.print_data_frame(cur_filters, ["Filter", "Constrain"], showindex=True)

    # Decide the filter that want to be removed
    instruction = "\nPlease select filter you want to remove: "
    values = list(str(i) for i in range(len(cur_filters)))
    index = wait_input(instruction, values)
    if index == -1 or index == len(cur_filters) - 1:
        return

    # Remove the corresponding filter in the constrains
    filter_name = cur_filters[int(index)][0]
    if filter_name == "Plan Type":
        constrains.pop(const.PLAN_TYPE)

    elif filter_name == "QHP Type":
        constrains.pop(const.QHP_TYPE)

    elif filter_name == "Child Option":
        constrains.pop(const.CHILD_ONLY)

    elif filter_name == "State":
        constrains.pop(const.PLAN_STATE)

    elif filter_name == "Metal Level":
        if insurance_type == "medical":
            detail_constrains.pop(const.M_METAL_LEVEL)
        else:
            detail_constrains.pop(const.D_METAL_LEVEL)

    elif filter_name == "Wellness Program":
        detail_constrains.pop(const.WELLNESS_OFFER)

    elif filter_name == "Pregnancy Notice":
        detail_constrains.pop(const.PREG_NOTICE)


def handle_find_avg_rate():
    """
    OPTION - Get Average Individual Rate for all available state.

    This option need receive "age" and "metal level" information from user.
    Then list the average individual rate for different state.
    """
    print("\n==============Average Individual Rate==============")

    # 1. Decide insurance type
    instruction = "\nWhich type of insurance do you want to query? (medical/dental): "
    values = ["medical", "dental"]
    insurance_type = wait_input(instruction, values)

    if insurance_type == -1:
        return

    # 2. Decide Metal Level
    instruction = "\nWhich metal level are you looking for:"
    if insurance_type == "medical":
        keys = list(Enum.m_metal_type.keys())
        utils.print_series(keys, "Metal Level", showindex=True)
    else:
        keys = list(Enum.d_metal_type.keys())
        utils.print_series(keys, "Metal Level", showindex=True)

    values = list(str(i) for i in range(len(keys)))
    value = wait_input(instruction, values)
    if value == -1:
        return
    metal_level_id = Enum.m_metal_type[keys[int(value)]] if insurance_type == "medical" \
        else Enum.d_metal_type[keys[int(value)]]

    # 3. Decide age for query
    instruction = "\nWhat is the age of searching? (1-99):"
    values = list(str(i) for i in range(1, 100))
    age = wait_input(instruction, values)

    if age == -1:
        return

    # 4. Get time intervals
    time_intervals = Query.get_time_intervals(metal_level_id=metal_level_id, age=age)
    utils.print_data_frame(time_intervals, ["Effective Date", "Expiration Date"], showindex=True)
    instruction = "\nPlease choose a time intervals:"
    values = list(str(i) for i in range(len(time_intervals)))
    index = wait_input(instruction, values)
    if index == -1:
        return
    index = int(index)
    effective_date = time_intervals[index][0]
    expiration_date = time_intervals[index][1]

    # 5. Query for results
    results = Query.get_avg_rate(metal_level_id=metal_level_id,
                                 age=age,
                                 effective_date=effective_date,
                                 expiration_date=expiration_date,
                                 insurance_type=insurance_type)
    utils.print_data_frame(results, ["State", "Individual Rate (average)"])

    input("\nPress any key to continue.")


def handle_search_eye_plan():
    """
    OPTION - Search Plan that covers Eye related benefits

    This option need "Age" information from user.
    And the option is able to provide plan information based on "Group", "Metal Level" and "Eye Benefits"
    """
    print("\n==============Eye Insurance Plan==============")

    # 1. Decides eye insurance plan type
    instruction = "\nWhich type of insurance do you want to query? :"
    options = ["Eye Exam", "Eye Glasses"]
    utils.print_series(options, "Option", showindex=True)
    values = list(str(i) for i in range(len(options)))
    value = wait_input(instruction, values)
    if value == -1:
        return
    insurance_type = options[int(value)]

    # 2. Decides groups
    instruction = "\nWhat is the group of searching? (Adult/ Child):"
    options = ["Adult", "Child"]
    utils.print_series(options, "Option", showindex=True)
    values = list(str(i) for i in range(len(options)))
    value = wait_input(instruction, values)
    if value == -1:
        return
    group_type = options[int(value)]

    # 3. Decides age
    instruction = "\nWhat is the age of searching? (1-99):"
    values = list(str(i) for i in range(1, 100))
    age = wait_input(instruction, values)
    if age == -1:
        return

    # 3. Decide Metal Level
    instruction = "\nWhich metal level are you looking for:"
    keys = list(Enum.m_metal_type.keys())
    utils.print_series(keys, "Metal Level", showindex=True)
    values = list(str(i) for i in range(len(keys)))

    value = wait_input(instruction, values)
    if value == -1:
        return
    metal_level_id = Enum.m_metal_type[keys[int(value)]]

    # Query for the result
    results = Query.get_eye_insurance(insurance_type=insurance_type, group_type=group_type, age=age,
                                      metal_level_id=metal_level_id)
    headers = ["Plan ID", "Effective Date", "Expiration Date", "Benefit Name", "Estimated Average",
               "Quantity Limit", "Unit Limit"]
    if results:
        instruction = "You can select a plan for detail information: "
        ind = display_in_pages(results, headers, instruction, showindex=True)
        if ind >= 0:
            plan_id = results[ind][0]
            search_plan_detail_information(plan_id)
    else:
        print("\nNo plans found.")
        input("\nPress any key to continue.")


def handle_search_benefit():
    """
    OPTION - Search Plans based on benefits

    This option would provide user all the available benefits.
    Then user is able to search all plans that cover this selected benefit.
    """

    # Search benefits list from database
    benefit_list = Query.get_benefit_list()

    # Select a benefit
    print("\n==============Plan Benefit==============")
    instruction = "Which benefit of do you want to query?:"
    ind = display_in_pages(benefit_list, ["Benefit"], instruction, showindex=True)
    if ind == -1:
        return
    benefit_type = benefit_list[int(ind)][0]

    # Query for the result
    results = Query.get_benefit(benefit_type=benefit_type)
    headers = ["Plan ID", "Benefit", "Quantity Limit", "Unit Limit"]
    if results:
        instruction = "You can select a plan for detail information: "
        ind = display_in_pages(results, headers, instruction, showindex=True)
        if ind >= 0:
            plan_id = results[ind][0]
            search_plan_detail_information(plan_id)
    else:
        print("\nNo plans found.")
        input("\nPress any key to continue.")


def handle_tobacco_search():
    """
    OPTION - Search Plans based on tobacco preference

    This option need "Age" information from user.
    Then it is able to find all plans based on user's tobacco preference
    """
    print("\n==============Tobacco User Friendly Insurance Plan==============")
    # age
    instruction = "\nWhat is the age of searching? (1-99):"
    values = list(str(i) for i in range(1, 100))
    age = wait_input(instruction, values)
    if age == -1:
        return

    # Wellness
    instruction = "\nDo you need tobacco wellness program? (yes/no):"
    values = ["yes", "no"]
    wellness = wait_input(instruction, values)
    if wellness == -1:
        return
    wellness_indicator = False
    if wellness == "yes":
        wellness_indicator = True

    # Print plans and select plan to get detail information
    results = Query.get_tobacco_insurance(wellness=wellness_indicator, age=age)
    headers = ["Plan ID", "Non Tobacco User Average Rate", "Tobacco User Average Rate"]
    if results:
        instruction = "You can select a plan for detail information: "
        ind = display_in_pages(results, headers, instruction, showindex=True)
        if ind >= 0:
            plan_id = results[ind][0]
            search_plan_detail_information(plan_id)
    else:
        print("\nNo plans found.")
        input("\nPress any key to continue.")


def display_in_pages(data, headers, instruction="", showindex=False):
    """
    Display data using pages

    :param data: data to be displayed
    :param headers: headers of the list
    :param instruction: instructions for the list
    :param showindex: whether to display index
    :return: select row index in data
             or -1 if not selected
    """
    pageindex = 0
    pagesize = 10
    total_rows = len(data)

    # Print plans based on pages
    while True:
        # Print plan for current page
        print()
        utils.print_data_frame(data_frame=data,
                               headers=headers,
                               pageindex=pageindex,
                               pagesize=pagesize,
                               showindex=showindex)

        # If open index, then allow user to select an index
        if showindex:
            values = list(str(i) for i in range(pagesize))
        else:
            values = list()

        if (pageindex + 1) * pagesize < total_rows:
            # Continue to display
            ins = "\nType 'it' for more information, use 'quit' to return.\n" + str(instruction)
            values.append("it")
        else:
            # Reach end of list
            ins = "\nReach end of the list, use 'quit' to return.\n" + str(instruction)

        cmd = wait_input(ins, values)
        if cmd == -1:
            return -1
        elif cmd == 'it':
            # Go to next page
            pageindex += 1
        else:
            # Return the selected item index in data
            cur_index = int(cmd)
            index = pageindex * pagesize + cur_index
            return index


def wait_input(instruction, values):
    """
    Waiting for user input

    :param instruction: instruction for user's input
    :param values: available input list
    :return: user input
    """
    tmp = input(instruction)
    # If user input 'quit', then return to menu
    if tmp.lower() == 'quit':
        return -1

    # Keep waiting correct input
    while tmp not in values:
        print("Invalid value, please try again.")
        tmp = input(instruction)
        if tmp.lower() == 'quit':
            return -1
    return tmp


def init(functions):
    functions.append([1, "Search Insurance Plan"])
    functions.append([2, "State Average Individual Rate"])
    functions.append([3, "Search Eye Plan"])
    functions.append([4, "Search Plan Benefits"])
    functions.append([5, "Search Tobacco User Friendly Plan"])


def main():
    print("Welcome to Healthcare Insurance Database System!")
    print("Data Source: The Centers for Medicare & Medicaid Services(CMS)")
    while True:
        print("\n==============Menu==============")
        functions = list()
        init(functions)
        print(tabulate(functions, ["Option", "Description"], tablefmt="fancy_grid"))
        index = input("\nPlease select an option:")
        if index.strip() == "1":
            handle_search_plan()
        elif index.strip() == "2":
            handle_find_avg_rate()
        elif index.strip() == "3":
            handle_search_eye_plan()
        elif index.strip() == "4":
            handle_search_benefit()
        elif index.strip() == "5":
            handle_tobacco_search()
        elif index == "quit":
            print("Bye.")
            exit(0)
        else:
            print("Invalid Index.")


if __name__ == '__main__':
    main()
