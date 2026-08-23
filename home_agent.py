import sys
import argparse
import traceback

from modules.finance import *
from modules.shopping import *
from modules.inventory import *
from modules.recipes import *
from modules.reminders import *

def main():
    parser = argparse.ArgumentParser(description='Home Agent CLI')
    parser.add_argument('--action', required=True, choices=[
        'expense', 'shopping', 'inventory', 'recipe', 'get_inventory', 'get_expenses', 
        'set_budget', 'get_balance', 'add_reminder', 'get_reminders', 'delete_reminder',
        'get_shopping_list', 'mark_bought', 'remove_shopping', 'clear_bought', 'bought',
        'get_expense_summary', 'weekly_report', 'save_recipe', 'extract_video',
        'get_recipes', 'read_recipe', 'delete_recipe', 'delete_expense'
    ])
    parser.add_argument('--doc_id', type=str, default="")
    parser.add_argument('--month', type=str, default="")
    parser.add_argument('--amount', type=float, default=0)
    parser.add_argument('--category', type=str, default="")
    parser.add_argument('--desc', type=str, default="")
    parser.add_argument('--item', type=str, default="")
    parser.add_argument('--qty', type=float, default=1)
    parser.add_argument('--unit', type=str, default="")
    parser.add_argument('--inv_action', choices=['add', 'use'], default='add')
    parser.add_argument('--ingredients', type=str, default="")
    parser.add_argument('--task', type=str, default="")
    parser.add_argument('--time', type=str, default="")
    parser.add_argument('--name', type=str, default="")
    parser.add_argument('--steps', type=str, default="")
    parser.add_argument('--url', type=str, default="")
    
    args = parser.parse_args()

    try:
        if args.action == 'expense': add_expense(args.amount, args.category, args.desc)
        elif args.action == 'delete_expense': delete_expense(args.doc_id)
        elif args.action == 'get_reminders': get_reminders()
        elif args.action == 'delete_reminder': delete_reminder(args.task)
        elif args.action == 'delete_recipe': delete_recipe(args.name)
        elif args.action == 'shopping': add_shopping_list(args.item, args.qty, args.unit, args.category)
        elif args.action == 'inventory': update_inventory(args.item, args.qty, args.inv_action, args.unit, args.category)
        elif args.action == 'recipe': generate_recipe(args.ingredients)
        elif args.action == 'get_inventory': get_inventory()
        elif args.action == 'get_expenses': get_expenses()
        elif args.action == 'set_budget': set_budget(args.amount, args.month)
        elif args.action == 'get_balance': get_balance(args.month)
        elif args.action == 'add_reminder': add_reminder(args.task, args.time)
        elif args.action == 'get_shopping_list': get_shopping_list()
        elif args.action == 'mark_bought': mark_as_bought(args.item)
        elif args.action == 'remove_shopping': remove_shopping_item(args.item)
        elif args.action == 'clear_bought': clear_shopping_list()
        elif args.action == 'bought': bought(args.item, args.qty, args.amount, args.category, args.unit)
        elif args.action == 'get_expense_summary': get_expense_summary(args.month)
        elif args.action == 'weekly_report': get_weekly_report()
        elif args.action == 'save_recipe': save_recipe(args.name, args.ingredients, args.steps, args.url)
        elif args.action == 'extract_video': extract_video_recipe(args.url)
        elif args.action == 'get_recipes': get_recipes()
        elif args.action == 'read_recipe': read_recipe(args.name)
    except Exception as e:
        print(f"Error executing {args.action}: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
