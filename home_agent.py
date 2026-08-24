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
        'get_recipes', 'read_recipe', 'delete_recipe', 'delete_expense',
        'add_asset', 'get_assets', 'add_bill', 'get_bills', 'get_expense_trend',
        'update_expense', 'update_category', 'batch_bought', 'delete_stock'
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
    parser.add_argument('--account', type=str, default="")
    parser.add_argument('--type', type=str, default="")
    parser.add_argument('--due_month', type=str, default="")
    parser.add_argument('--recurring', type=str, default="")
    parser.add_argument('--old_name', type=str, default="")
    parser.add_argument('--json_data', type=str, default="")
    
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
        elif args.action == 'add_reminder': add_reminder(args.task, args.time, args.recurring)
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
        elif args.action == 'add_asset': add_asset(args.account, args.amount, args.type)
        elif args.action == 'get_assets': get_assets()
        elif args.action == 'add_bill': add_bill(args.item, args.amount, args.due_month, args.recurring)
        elif args.action == 'get_bills': get_bills(args.month)
        elif args.action == 'get_expense_trend': get_expense_trend(args.category)
        elif args.action == 'update_expense': update_expense(args.old_name, args.amount, args.category, args.desc)
        elif args.action == 'update_category': update_category(args.item, args.category)
        elif args.action == 'batch_bought': batch_bought(args.json_data)
        elif args.action == 'delete_stock': delete_stock(args.item)
        
    except Exception as e:
        print(f"❌ Error saat mengeksekusi {args.action}: {str(e)}")
        print("\nStacktrace:")
        traceback.print_exc()

if __name__ == '__main__':
    main()
