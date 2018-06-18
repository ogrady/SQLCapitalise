import psqlparse

class Visitor(object):
    def visit(self, node):
        self._visit(node)

    def _visit(self, node):
        if not node:
            return
        fname = "visit_%s" % (type(node).__name__,)
        if hasattr(self, fname):
            func = getattr(self, fname)
            func(node)
        else:
            self.visit_generic(node)

    def visit_generic(self, node):
        raise Exception("Visit not implemented for type '%s'." % (type(node),))

    def visit_list(self, node):
        for n in node:
            self._visit(n)

    def visit_dict(self, node):
        print(node.keys())

    def visit_tuple(self, node):
        self.visit_list(self, node)

class PrettyPrinter(Visitor):
    def __init__(self, indentSize = 2):
        self.s = ""
        self.currentIndent = ""
        self.indent = "".join([" " for _ in range(indentSize)])

    def inc(self):
        self.currentIndent += self.indent

    def dec(self):
        self.currentIndent = self.currentIndent[:-len(self.currentIndent)]

    def lbr(self, inc = False, dec = False):
        self.s += "\n"
        if inc:
            self.inc()
        if dec:
            self.dec()
        self.s += self.currentIndent

    def p(self, s, spaceAfter = True):
        self.s += str(s)
        if spaceAfter:
            self.s += " "

    def visit(self, node):
        self.s = ""
        self._visit(node)
        return self.s

    def visit_generic(self, node):
        print("t:" + type(node).__name__)
        print("d:" + str(dir(node)))

    def visit_str(self, node):
        self.p(node)

    def visit_int(self, node):
        self.p(node)

    def visit_float(self, node):
        self.p(node)

    def visit_SelectStmt(self, node):
        self._visit(node.with_clause)
        self.p("SELECT")
        self.lbr(inc = True)
        self._visit(node.distinct_clause)
        self._visit(node.into_clause)
        self._visit(node.target_list)
        self.lbr(dec = True)
        if node.from_clause:
            self.p("FROM")
            self.lbr(inc = True)
            self._visit(node.from_clause)
            self.lbr(dec = True)
        if node.where_clause:
            self.p("WHERE")
            self.lbr(inc = True)
            self._visit(node.where_clause)
            self.lbr(dec = True)
        if node.group_clause:
            self.p("GROUP BY")
            self._visit(node.group_clause)
        if node.having_clause:
            self.p("HAVING")
            self._visit(node.having_clause)
        if node.window_clause:
            self._visit(node.window_clause)
        self._visit(node.values_lists)
        if node.sort_clause:
            self.p("ORDER BY")
            self._visit(node.sort_clause)
        if node.limit_offset:
            self.p("LIMIT")
            self._visit(node.limit_offset)
        # self._visit(node.limit_count)
        self._visit(node.locking_clause)
        

    def visit_InsertStmt(self, node):
        self.p("INSERT")
        self._visit(node.relation)
        self._visit(node.cols)
        self._visit(node.select_stmt)
        self._visit(node.on_conflict_clause)
        self._visit(node.returning_list)
        self._visit(node.with_clause)

    def visit_UpdateStmt(self, node):
        self.p("UPDATE")
        self._visit(node.relation)
        self._visit(node.target_list)
        self._visit(node.where_clause)
        self._visit(node.from_clause)
        self._visit(node.returning_list)
        self._visit(node.with_clause)

    def visit_DeleteStmt(self, node):
        self.p("DELETE FROM")
        self._visit(node.relation)
        self._visit(node.using)
        self._visit(node.where)
        self._visit(node.returning_list)
        self._visit(node.with_clause)

    def visit_WithClause(self, node):
        self.p("WITH")
        if node.recursive:
            pass
        self._visit(node.ctes)

    # util parse nodes
    def visit_ResTarget(self, node):
        self._visit(node.val)
        if node.name:
            self.p("AS %s" % (node.name,))

    def visit_ColumnRef(self, node):
        for f in node.fields:
            self._visit(f)
        # self.location?

    def visit_AStar(self, node):
        self.p("*")

    def visit_AExpr(self, node):
        self._visit(node.lexpr)
        self._visit(node.name)
        self._visit(node.rexpr)

    def visit_BoolExpr(self, node):
        self._visit(node.args)
        self._visit(node.boolop)

    def visit_AConst(self, node):
        self.p(node.val)

    def visit_String(self, node):
        self.p(node.val)

    # prim
    def visit_RangeVar(self, node):
        name = node.relname
        if node.schemaname:
            name = "%s.%s" % (node.schemaname, name)
        if node.catalogname:
            name = "%s.%s" % (node.catalogname, name)
        self.p(name)

        if node.alias:
            self.p("AS")
            self.visit(node.alias)

    def visit_Alias(self, node):
        self.p(node.aliasname)
        if node.colnames:
            self.p("(", spaceAfter = False)
            for c in node.colnames:
                self._visit(c)
            self.p(")")

def pprint(sql):
    stmts = psqlparse.parse(sql)
    return PrettyPrinter().visit(stmts)
