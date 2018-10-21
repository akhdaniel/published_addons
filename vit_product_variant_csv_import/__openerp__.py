{
    'name': 'Product Variant CSV Import',
    'version': '0.1',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': 'Add menu entry to allow CSV import of templates with variants',
    'description': """
This module adds a menu entry in *Sales > Configuration > Product Categories and attributes > Product Template CSV Import", that will work with the import of CSV file product.template.csv that contains variants.

Steps:
-----------------
1. Import Attributes: eg Size, Color
2. Import Attribute Values: eg Size: X,M,L,etc or Color:White, Blue, etc
3. Import Product Templates with Variants

This module has been originally written by Alexis de Lattre from Akretion
<alexis.delattre@akretion.com>. Ported to Odoo version 10 by vitraining.com


            Find our other interesting modules that can make your life easier:
            https://www.odoo.com/apps/modules/browse?search=vitraining
        
        
    """,
    'author': 'vitraining.com',
    'website': 'http://www.vitraining.com',
    'depends': ['product'],
    'data': ['product_view.xml'],
}
